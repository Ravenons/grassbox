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

class Process(object):
  """ Representation of a Process

  Attributes:
    pid: Process number
    name: Process name
    opened_files: Dictionary with handle -> filename pairs
  """

  def __init__(self, pid, name):
    """ Inits Process with his pid and name.

    Args:
      pid: PID of the analyzed process.
      name: Filename of the analyzed process.
    """
    self.pid = pid
    self.name = name
    self.opened_files = {}

  def get_filename_from_handle(self, handle):
    """ Returns the filename associated with the handle provided.

    Args:
      handle: Handle associated with the file.
    """
    return self.opened_files[handle]

  def add_opened_file(self, filename, handle):
    """ Adds a new file opened to the process with the specified filename and handle.

    Args:
      filename: Name of the file.
      handle: Handle associated with the file.
    """
    self.opened_files[handle] = filename

  def remove_closed_file(self, handle):
    """ Remove the file opened with the handle provided from the process. """
    if handle in self.opened_files:
      del self.opened_files[handle]


class GrassboxReport(object):
  """ Report: Parser and generator.

  Attributes:
    input: File where the Dtrace output is located
    output: File where the Grassbox report is gonna to be written
    original_pid: PID from the process analyzed by Grassbox
    processes_created: Dictionary with PID -> Processes pairs, representing the processes created by the analyzed process
    files_opened: List of files opened by the analyzed process
    files_read: List of files read by the analyzed process
    files_writed: List of files written by the analyzed process
    files_blacklist: List of files blacklisted in Grassbox, for omit them
  """

  def __init__(self, dtrace_output_path, report_path, original_name,
               original_pid):
    """ Inits the Report.

    Args:
      dtrace_output_path: Location of the dtrace output file
      report_path: Destination of the report
      original_name: Name of the process analyzed
      original_pid: PID of the process analyzed
    """

    self.input = open(dtrace_output_path, 'r')
    self.output = open(report_path, 'w')
    self.original_pid = original_pid

    self.processes_created = \
      {original_pid: Process(original_pid, original_name)}
    self.files_opened = []
    self.files_read = []
    self.files_writed = []
    self.files_blacklist = ['/dev/dtracehelper', '.']

  def __del__(self):
    """ Destroy the Report. """
    # Closes the Dtrace output file (input) and report output file (output).
    self.input.close()
    self.output.close()

  def parse_dtrace_output(self):
    """ Parse the dtrace output file and process it. """
    current_line = self.input.readline()

    # Process every item, one at a time
    while current_line != '':
      # First line in an item, pid associated to the event
      pid = int(current_line)

      # Second line in an item, event class
      current_line = self.input.readline()

      # Naive approach, just taking into account new processes
      if pid >= self.original_pid:
        if current_line == 'PROCESS\n':
          self._parse_process_item(pid)
        elif current_line == 'FILE\n':
          self._parse_file_item(pid)
      else:
        self._skip_until_empty_line()

      current_line = self.input.readline()

  def write_report(self):
    """ Writes the report to the output file (self.output). """
    self.output.write(
      '############\n# PROCESSES CREATED \n############' + '\n\n')

    for process_pid in self.processes_created:
      self.output.write('\t' + str(process_pid) + ': ' +
                        self.processes_created[process_pid].name + '\n')

    self.output.write('\n############\n# FILES OPENED \n############' + '\n\n')
    for opened_file in self.files_opened:
      self.output.write('\t' + opened_file + '\n')

    self.output.write('\n############\n# FILES READ \n############' + '\n\n')
    for read_file in self.files_read:
      self.output.write('\t' + read_file + '\n')

    self.output.write('\n############\n# FILES WRITTEN \n############' + '\n\n')
    for writed_file in self.files_writed:
      self.output.write('\t' + writed_file + '\n')

  def _parse_process_item(self, _pid):
    # Third line in an item, event subclass
    current_line = self.input.readline()
    if current_line == 'CREATE\n':
      process_name = self.input.readline()
      process_pid = self.input.readline()
      self._insert_created_process(int(process_pid), process_name.strip('\n'))
      self.input.readline()

  def _parse_file_item(self, pid):
    current_line = self.input.readline()
    if current_line == 'OPEN\n':
      file_handle = self.input.readline()
      file_path = self.input.readline()
      self._insert_opened_file(int(file_handle), file_path.strip('\n'), pid)
      self.input.readline()
    elif current_line == 'READ\n':
      file_handle = self.input.readline()
      self._insert_read_file(int(file_handle), pid)
      self.input.readline()
    elif current_line == 'WRITE\n':
      file_handle = self.input.readline()
      self._insert_writed_file(int(file_handle), pid)
      self.input.readline()
    elif current_line == 'CLOSE\n':
      file_handle = self.input.readline()
      self._remove_closed_file(int(file_handle), pid)
      self.input.readline()

  def _insert_opened_file(self, file_handle, file_path, pid):
    """ Insert a new file opened to the report.

    Params:
      file_handle: The file handle.
      file_path: Location of the file.
      pid: PID of the process that have opened the file.
    """
    self.processes_created[pid].add_opened_file(file_path, file_handle)
    if (not file_path in self.files_opened) \
        and (not file_path in self.files_blacklist):
      self.files_opened.append(file_path)

  def _remove_closed_file(self, file_handle, pid):
    self.processes_created[pid].remove_closed_file(file_handle)

  def _insert_read_file(self, file_handle, pid):
    """ Insert a new file read to the report.

    Params:
      file_handle: The file handle.
      pid: PID of the process that have read the file.
    """
    file_path = \
      self.processes_created[pid].get_filename_from_handle(file_handle)
    if (not file_path in self.files_read) \
        and (not file_path in self.files_blacklist):
      self.files_read.append(file_path)

  def _insert_writed_file(self, file_handle, pid):
    """ Insert a new file written to the report.

    Params:
      file_handle: The file handle.
      pid: PID of the process that wrote the file.
    """
    file_path = \
      self.processes_created[pid].get_filename_from_handle(file_handle)
    if (not file_path in self.files_writed) \
        and (not file_path in self.files_blacklist):
      self.files_writed.append(file_path)

  def _insert_created_process(self, process_pid, process_name):
    """ Insert a new process created to the report.

    Params:
      process_pid: PID of the process.
      process_name: Name of the process.
    """
    self.processes_created[process_pid] = Process(process_pid, process_name)

  def _skip_until_empty_line(self):
    current_line = self.input.readline()
    while current_line != '\n':
      current_line = self.input.readline()