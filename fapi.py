#!/usr/bin/env python


import sys
import argparse
import base64
import getpass 

from os.path import expanduser

import ConfigParser

__program__ = 'fapi'
__version__ = 'VERSION_DEVEL' # Replaced by a Makefile target

class Fapi(object):
  """The main F5 API Tool Object """

  __f5api_user = ''
  __f5api_pass = ''

  def __init__(self, config_file):
    config = ConfigParser.ConfigParser()
    config.read(config_file)

    if config.has_option('fapi', 'user'):
      __f5api_user = config.get('fapi', 'user')
    else:
      __f5api_user = getpass.getuser()

    if config.has_option('fapi', 'pass64'):
      __f5api_pass = base64.decodestring(config.get('fapi', 'pass64'))
    else:
      prompt = 'Enter API password for user ' + __f5api_user + ': '
      __f5api_pass = getpass.getpass(prompt)

    print __f5api_pass


if __name__ == '__main__':
  """ The main function, here we will have Popcorn for free! """
  
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', action='store_true', help='Verbose')
  parser.add_argument('-V', action='store_true', help='Print version')
  parser.add_argument('-C', action='store', help='Config file',
    default=expanduser('~') + '/.fapi.conf')
  args = vars(parser.parse_args())
  
  if args['v']:
    print 'Verbose'
  if args['V']:
    print 'This is ' + __program__ + ' version ' + __version__

  fapi = Fapi(args['C'])


