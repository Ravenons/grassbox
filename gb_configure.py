#!/usr/bin/python

import os
import pickle


def main():
  print('Dumping current user environment...')
  config = open('grassbox.conf', 'w')
  # pickle.dump was not working...
  config.write(pickle.dumps(os.environ))
  config.close()
  print('Finished')


if __name__ == '__main__':
  main()
