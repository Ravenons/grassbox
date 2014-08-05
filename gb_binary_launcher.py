# The MIT-Zero License
#
# Copyright (c) 2014 Carlos Ledesma, Jose Toro
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import subprocess
import os
import pickle
import pwd

def launch_binary(binary_path):
  """ Launchs the binary in a new process.

  Params:
    binary_path: Location of the binary.
  """
  # open current configuration (right now, just regular user environment)
  config = open('grassbox.conf', 'r')
  env = pickle.loads(config.read())

  # UNIX's password database for a particular user
  pw_db = pwd.getpwnam(env['USER'])

  # get uid and gid from loaded environment
  uid = pw_db.pw_uid
  gid = pw_db.pw_gid

  # cwd still not implemented / cwd=os.path.dirname(binary_path[0]),
  # do we really need to close inherited fds? / close_fds=True,
  # too much noise at dtrace_output.txt, subprocess library
  # closes about 10k handles...
  child_process = subprocess.Popen(binary_path,
                                   preexec_fn=change_user(uid, gid),
                                   env=env)

  return child_process.pid

def change_user(uid, gid):
  """ Set the UID and GID for the new process.

  Params:
    uid: UID of the user.
    gid: GID of the user.
  """
  def my_callback():
    os.setgid(gid)
    os.setuid(uid)

  return my_callback