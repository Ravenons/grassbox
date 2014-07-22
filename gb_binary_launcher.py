import subprocess
import os
import pickle
import pwd

def launch_binary(binary_path):
  # open current configuration (right now, just regular user environment)
  config = open('grassbox.conf', 'r')
  env = pickle.loads(config.read())

  # UNIX's password database for a particular user
  pw_db = pwd.getpwnam(env['USER'])

  # get uid and gid from loaded environment
  uid = pw_db.pw_uid
  gid = pw_db.pw_gid

  # cwd still not implemented
  child_process = subprocess.Popen(binary_path,
                                   preexec_fn=change_user(uid, gid), env=env)

  return child_process.pid


def change_user(uid, gid):
  def my_callback():
    os.setgid(gid)
    os.setuid(uid)

  return my_callback