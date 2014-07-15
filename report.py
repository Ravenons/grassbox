class GrassboxReport(object):
  def __init__(self):
    self.opened_files = []

  def insert_opened_file(self, opened_file):
    if not opened_file in self.opened_files:
      self.opened_files.append(opened_file)

  def print_report(self):
    print '############\nOpened files\n############'
    for opened_file in self.opened_files:
      print opened_file


class ReportCreation(object):
  def __init__(self):
    self.report = GrassboxReport()

  def item_receiver(self, item):
    item_parsed = item.split(item, '\n')
    if item_parsed[0] == 'FILE':
      if item_parsed[1] == 'OPEN':
        self.report.insert_opened_file(item_parsed[2])


