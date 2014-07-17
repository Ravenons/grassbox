class GrassboxReport(object):
  def __init__(self, dtrace_output_path, report_path, original_name,
               original_pid):

    self.input = open(dtrace_output_path, 'r')
    self.output = open(report_path, 'w')
    self.original_pid = original_pid

    self.process_create = {original_pid: original_name}
    self.file_open = []

  def __del__(self):

    self.input.close()
    self.output.close()

  def parse_dtrace_output(self):

    current_line = self.input.readline()
    while current_line != '':

      pid = int(current_line)

      current_line = self.input.readline()
      if pid in self.process_create:
        if current_line == 'PROCESS\n':
          self._parse_process_item()
        elif current_line == 'FILE\n':
          self._parse_file_item()
      else:
        self._skip_until_empty_line()

      current_line = self.input.readline()

  def write_report(self):

    self.output.write('############\n# process_create \n############' + '\n')
    for process_pid in self.process_create:
      self.output.write('\t' + str(process_pid) + ': ' +
                        self.process_create[process_pid] + '\n')

    self.output.write('\n############\n# file_open\n############' + '\n')
    for opened_file in self.file_open:
      self.output.write('\t' + opened_file + '\n')

  def _parse_process_item(self):
    current_line = self.input.readline()
    if current_line == 'CREATE\n':
      process_name = self.input.readline()
      process_pid = self.input.readline()
      self._insert_created_process(process_name.strip('\n'), int(process_pid))
      self.input.readline()

  def _parse_file_item(self):
    current_line = self.input.readline()
    if current_line == 'OPEN\n':
      current_line = self.input.readline()
      self._insert_opened_file(current_line.strip('\n'))
      self.input.readline()

  def _insert_opened_file(self, opened_file):
    if not opened_file in self.file_open:
      self.file_open.append(opened_file)

  def _insert_created_process(self, process_name, process_pid):
    self.process_create[process_pid] = process_name

  def _skip_until_empty_line(self):
    current_line = self.input.readline()
    while current_line != '\n':
      current_line = self.input.readline()