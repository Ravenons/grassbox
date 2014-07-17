#!/usr/bin/python

import gb_dtrace_wrapper
import gb_binary_launcher
import gb_report

import multiprocessing
import os


def main():
  dtrace_script_path = 'main_script.d'  # file path to DTrace program
  dtrace_output_path = 'dtrace_output.txt'  # file path to write DTrace program output
  dtrace_runtime = 5  # approximate time Dtrace program will run
  binary_path = 'man'
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

  # launch binary
  original_pid = gb_binary_launcher.launch_binary(binary_path)

  # debug purposes
  print 'Original binary PID: ' + str(original_pid)

  p.join()

  # create report
  report = gb_report.GrassboxReport(dtrace_output_path, report_path,
                                    os.path.basename(binary_path),
                                    int(original_pid))

  report.parse_dtrace_output()
  report.write_report()


if __name__ == '__main__':
  main()
