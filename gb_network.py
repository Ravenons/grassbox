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


class NetworkReport(object):
  """ Network Report Generator.

  Attributes:
    outputFile: Location where the Network report is gonna to be written.
    tcp_out: Temporal file where tcpdump output will be located.
    monitor: The tcpdump process.
  """
  def __init__(self, outputFile='network.txt'):
    """ Inits the report.

    Args:
      outputFile: Location where the Network report is gonna to be written.
    """

    self.outputFile = outputFile
    self.tcp_out = open('tcpdump.out', 'w')
    self.monitor = subprocess.Popen(('tcpdump', '-nl'), stdout=self.tcp_out)

  def finish(self):
    """ Stops the network monitoring and closes the temporal file. """
    self.monitor.kill()
    self.tcp_out.close()

  def generate(self):
    """ Parses the tcpdump output to the report file (outputFile) """
    report = open('tcpdump.out', 'r')
    out = open(self.outputFile, 'w')

    out.write("###########################\n")
    out.write("# Connections Established #\n")
    out.write("###########################\n\n")
    out.flush()

    p1 = subprocess.Popen(('cut', '-d', ' ', '-f2', '-f5'), stdin=report, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(('sed', 's/.$//'), stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen('sort', stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen('uniq', stdin=p3.stdout, stdout=out)

    p4.wait()

    out.close()



