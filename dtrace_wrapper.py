from ctypes import CDLL, Structure, CFUNCTYPE, POINTER, byref, c_int, c_char, \
  c_uint, c_char_p, c_void_p
import time

# load the native library for DTrace
libdtrace = CDLL('libdtrace.dylib')


# ###############################################################################
# some C structures needed
# (only buffered is used right now
# ###############################################################################

class dtrace_bufdata(Structure):
  _fields_ = [("dtbda_handle", c_void_p),
              ("dtbda_buffered", c_char_p),
              ("dtbda_probe", c_void_p),
              ("dtbda_recdesc", c_void_p),
              ("dtbda_aggdata", c_void_p),
              ("dtbda_flags", c_uint)]


class dtrace_probedesc(Structure):
  _fields_ = [("dtrace_id_t", c_uint),
              ("dtpd_provider", c_char),
              ("dtpd_mod", c_char),
              ("dtpd_func", c_char_p),
              ("dtpd_name", c_char_p)]


class dtrace_probedata(Structure):
  _fields_ = [("dtpda_handle", c_void_p),
              ("dtpda_edesc", c_void_p),
              ("dtpda_pdesc", dtrace_probedesc),
              ("dtpda_cpu", c_int),
              ("dtpda_data", c_void_p),
              ("dtpda_flow", c_void_p),
              ("dtpda_prefix", c_void_p),
              ("dtpda_indent", c_int)]


class dtrace_recdesc(Structure):
  _fields_ = [("dtrd_offset", c_uint)]

# ###############################################################################
# callbacks signatures and callbacks definitions
# (only buffered is used right now)
# ###############################################################################

buffered_signature = CFUNCTYPE(c_int,
                               POINTER(dtrace_bufdata),
                               POINTER(c_void_p))

chew_signature = CFUNCTYPE(c_int,
                           POINTER(dtrace_probedata),
                           POINTER(c_void_p))

chewrec_signature = CFUNCTYPE(c_int,
                              POINTER(dtrace_probedata),
                              POINTER(dtrace_recdesc),
                              POINTER(c_void_p))


def buffered(bufdata, arg):
  print bufdata.contents.dtbda_buffered
  return 0


def chew(data, arg):
  return 0


def chewrec(data, rec, arg):
  if rec is None:
    return 1
  return 0

################################################################################
# Methods imported from dlibtrace, signatures definitions
################################################################################

# error getters (I use c_void_p as there's no need to know the structure)
libdtrace.dtrace_errmsg.argtypes = [c_void_p, c_int]
libdtrace.dtrace_errmsg.restype = c_char_p
libdtrace.dtrace_errno.argtypes = [c_void_p]
libdtrace.dtrace_errno.restype = c_int


# open DTrace's handle
libdtrace.dtrace_open.argtypes = [c_int, c_int, POINTER(c_int)]
libdtrace.dtrace_open.restype = c_void_p


# modify DTrace options
libdtrace.dtrace_setopt.argtypes = [c_void_p, c_char_p, c_char_p]
libdtrace.dtrace_setopt.restype = c_int


# register simple output callback
libdtrace.dtrace_handle_buffered.argtypes = [c_void_p, buffered_signature,
                                             c_void_p]
libdtrace.dtrace_handle_buffered.restype = c_int


# handle close
libdtrace.dtrace_close.argtypes = [c_void_p]
libdtrace.dtrace_close.restype = None


# compile
libdtrace.dtrace_program_fcompile.argtypes = [c_void_p, c_void_p, c_int,
                                              c_int, POINTER(c_char_p)]
libdtrace.dtrace_program_fcompile.restype = c_void_p


# execute
libdtrace.dtrace_program_exec.argtypes = [c_void_p, c_void_p, c_void_p]
libdtrace.dtrace_program_exec.restype = c_int


# go
libdtrace.dtrace_go.argtypes = [c_void_p]
libdtrace.dtrace_go.restype = c_int


# sleep
libdtrace.dtrace_sleep.argtypes = [c_void_p]
libdtrace.dtrace_sleep.restype = None


# work
libdtrace.dtrace_work.argtypes = [c_void_p, c_void_p, chew_signature,
                                  chewrec_signature, c_void_p]
libdtrace.dtrace_work.restype = c_int


# stop
libdtrace.dtrace_stop.argtypes = [c_void_p]
libdtrace.dtrace_stop = c_int


class DTraceWrapper(object):
  def __init__(self):

    self.chew_wrapped = chew_signature(chew)
    self.chewrec_wrapped = chewrec_signature(chewrec)
    self.buffered_wrapped = buffered_signature(buffered)

    # get handle (the line just below is just an error code passed by reference)
    errorcode = c_int()

    # $1 = DTrace version, $2 = Mac OS X flags (see open source OS X dtrace(1))
    self.handle = libdtrace.dtrace_open(3, 4, byref(errorcode))
    if not self.handle:
      raise Exception('dtrace_open() failed, ' +
                      libdtrace.dtrace_errmsg(None, errorcode))

    # set buffer options
    if libdtrace.dtrace_setopt(self.handle, 'bufsize', '4m') != 0:
      raise Exception(
        'dtrace_setopt() failed, ' + self.last_error_msg(self.handle))

    # set simple output callbacks
    if libdtrace.dtrace_handle_buffered(self.handle, self.buffered_wrapped,
                                        None):
      raise Exception('dtrace_handle_buffered() failed, ' +
                      self.last_error_msg(self.handle))

  def __del__(self):

    # don't forget to close the handle
    libdtrace.dtrace_close(self.handle)

  # get the last and most important error
  def last_error_msg(self, handle):

    return libdtrace.dtrace_errmsg(handle, libdtrace.dtrace_errno(handle))

  def run_script(self, script, runtime):

    # compile
    prg = libdtrace.dtrace_program_fcompile(self.handle,
                                            script, 0, 0, None)
    if prg is None:
      raise Exception('dtrace_program_strcompile() failed, ' +
                      self.last_error_msg(self.handle))

    # start
    if libdtrace.dtrace_program_exec(self.handle, prg, None):
      raise Exception('dtrace_program_exec() failed, ' +
                      self.last_error_msg(self.handle))
    if libdtrace.dtrace_go(self.handle):
      raise Exception('dtrace_go() failed, ' + self.last_error_msg(self.handle))

    # main loop
    initialtime = time.time()
    while time.time() - initialtime < runtime:
      libdtrace.dtrace_sleep(self.handle)
      libdtrace.dtrace_work(self.handle, None, self.chew_wrapped,
                            self.chewrec_wrapped, None)

    libdtrace.dtrace_stop(self.handle)