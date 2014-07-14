#!/usr/bin/python

from dtrace_wrapper import DTraceWrapper
from ctypes import CDLL, c_int, c_char_p, c_void_p

# import the native C standard library
libc = CDLL('libc.dylib')

# define function signatures
libc.fopen.argtypes = [c_char_p, c_char_p]
libc.fopen.restype = c_void_p
libc.fclose.argtypes = [c_void_p]
libc.fclose.restype = c_int


def main():
  # create the DTrace wrapper
  dtrace = DTraceWrapper()

  # open file
  SCRIPT = libc.fopen('main_script.d', 'r')

  # run script for some seconds
  dtrace.run_script(SCRIPT, 10)

  # close file
  libc.fclose(SCRIPT)


if __name__ == '__main__':
  main()
