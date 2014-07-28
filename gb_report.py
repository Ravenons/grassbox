class Process(object):
  def __init__(self, pid, name):
    self.pid = pid
    self.name = name
    self.opened_files = {}

  def get_filename_from_handle(self, handle):
    return self.opened_files[handle]

  def add_opened_file(self, filename, handle):
    self.opened_files[handle] = filename

  def remove_closed_file(self, handle):
    if handle in self.opened_files:
      del self.opened_files[handle]


class GrassboxReport(object):
  def __init__(self, dtrace_output_path, report_path, original_name,
               original_pid):

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

    self.input.close()
    self.output.close()

  def parse_dtrace_output(self):

    current_line = self.input.readline()
    # process every item, one at a time
    while current_line != '':

      # first line in an item, pid associated to the event
      pid = int(current_line)

      # second line in an item, event class
      current_line = self.input.readline()

      # naive approach, just taking into account new processes
      if pid >= self.original_pid:
        if current_line == 'PROCESS\n':
          self._parse_process_item(pid)
        elif current_line == 'FILE\n':
          self._parse_file_item(pid)
      else:
        self._skip_until_empty_line()

      current_line = self.input.readline()

  def write_report(self):

    self.output.write(
      '############\n# CREATED PROCESSES \n############' + '\n\n')
    for process_pid in self.processes_created:
      self.output.write('\t' + str(process_pid) + ': ' +
                        self.processes_created[process_pid].name + '\n')

    self.output.write('\n############\n# OPENED FILES \n############' + '\n\n')
    for opened_file in self.files_opened:
      self.output.write('\t' + opened_file + '\n')

    self.output.write('\n############\n# READ FILES \n############' + '\n\n')
    for read_file in self.files_read:
      self.output.write('\t' + read_file + '\n')

    self.output.write('\n############\n# WRITED FILES \n############' + '\n\n')
    for writed_file in self.files_writed:
      self.output.write('\t' + writed_file + '\n')

  def _parse_process_item(self, _pid):

    # third line in an item, event subclass
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
    self.processes_created[pid].add_opened_file(file_path, file_handle)
    if (not file_path in self.files_opened) \
        and (not file_path in self.files_blacklist):
      self.files_opened.append(file_path)

  def _remove_closed_file(self, file_handle, pid):
    self.processes_created[pid].remove_closed_file(file_handle)

  def _insert_read_file(self, file_handle, pid):
    file_path = \
      self.processes_created[pid].get_filename_from_handle(file_handle)
    if (not file_path in self.files_read) \
        and (not file_path in self.files_blacklist):
      self.files_read.append(file_path)

  def _insert_writed_file(self, file_handle, pid):
    file_path = \
      self.processes_created[pid].get_filename_from_handle(file_handle)
    if (not file_path in self.files_writed) \
        and (not file_path in self.files_blacklist):
      self.files_writed.append(file_path)

  def _insert_created_process(self, process_pid, process_name):
    self.processes_created[process_pid] = Process(process_pid, process_name)

  def _skip_until_empty_line(self):
    current_line = self.input.readline()
    while current_line != '\n':
      current_line = self.input.readline()