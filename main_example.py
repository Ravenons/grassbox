#!/usr/bin/python

import dtrace_wrapper

def main():
  script_path = 'main_script.d'  # file path to DTrace program
  output_path = 'output.txt'  # file path to write DTrace program output
  runtime = 10  # approximate time Dtrace program will run

  # run DTrace script
  dtrace_wrapper.run(script_path, output_path, runtime)

if __name__ == '__main__':
  main()
