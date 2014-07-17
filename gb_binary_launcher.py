import subprocess


def launch_binary(binary_path):
  child_process = subprocess.Popen(binary_path)
  return child_process.pid