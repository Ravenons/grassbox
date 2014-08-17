#!/usr/bin/python

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

import gb_dtrace_wrapper
import gb_binary_launcher
import gb_report
import gb_network

import multiprocessing
import os
import sys

def main():
  """ Grassbox main script. """

  dtrace_script_path = 'main_script.d'      # file path to DTrace program
  dtrace_output_path = 'dtrace_output.txt'  # file path to write DTrace program output
  dtrace_runtime = 3                        # approximate time Dtrace program will run

  # Debug -> Change to params later
  binary_path = ['./orwc']

  # report.txt can be default option -> Change to accept alternatives
  report_path = 'report.txt'

  if os.path.exists(dtrace_output_path):
    os.remove(dtrace_output_path)
  if os.path.exists(report_path):
    os.remove(report_path)

  # debug purposes
  print 'Python interpreter PID: ' + str(os.getpid())

  # start tracing
  gb_dtrace_wrapper.start_tracing(dtrace_script_path)

  # collect traces
  p = multiprocessing.Process(target=gb_dtrace_wrapper.log_to_file,
                              args=(dtrace_output_path, dtrace_runtime))
  p.start()

  # start network monitoring
  network = gb_network.NetworkReport()

  # launch binary
  original_pid = gb_binary_launcher.launch_binary(binary_path)

  # debug purposes
  print 'Original binary PID: ' + str(original_pid)

  # wait process to finish
  p.join()
  
  # stop network monitoring
  network.finish()

  # generate dtrace report
  print('Generating DTrace report...')
  report = gb_report.GrassboxReport(dtrace_output_path, report_path,
                                    os.path.basename(binary_path[0]),
                                    int(original_pid))

  report.parse_dtrace_output()
  report.write_report()

  # generate network report
  print('Generating Network report...')
  network.generate()

  print('Done!')

if __name__ == '__main__':
  main()
