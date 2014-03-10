#!/usr/bin/env python

# 2014 (c) Paul Buetow

import argparse
import base64
import getpass 
import sys

from os.path import expanduser

import ConfigParser

__program__ = 'fapi'
__version__ = 'VERSION_DEVEL' # Replaced by a Makefile target

class Fapi(object):
    '''The main F5 API Tool Object '''

    config = None
    __f5api_user = ''
    __f5api_pass = ''

    def __init__(self, args):
        ''' Initialize the config file, username and password '''

        if args['v']:
            print 'Reading configuration'

        config_file = args['C']

        config = ConfigParser.ConfigParser()
        config.read(config_file)

        self.__args_merge(config, args)

        if config.has_option('fapi', 'user'):
            self.__f5api_user = config.get('fapi', 'user')
        else:
            self.__f5api_user = getpass.getuser()

        if config.has_option('fapi', 'pass64'):
            self.__f5api_pass = base64.decodestring(
                                config.get('fapi', 'pass64'))
        else:
            prompt = 'Enter API password for user ' + self.__f5api_user + ': '
            self.__f5api_pass = getpass.getpass(prompt)

        self.__login()


    def __args_merge(self, config, args):
        ''' Merges args to the config object '''

        if not config.has_section('args'):
            config.add_section('args')

        for k, v in args.items():
            if args['v']: print "Set arg %s: %s" % (k, v)
            config.set('args', k, str(v))

        self.config = config


    def __login(self):
        ''' Logs into the F5 BigIP SOAP API '''

        if self.config.getboolean('args', 'v'):
            print 'Login to BigIP API'

        apiuri = self.config.get('fapi', 'apiuri')
        # ... to be done


if __name__ == '__main__':
    ''' The main function, here we will have Popcorn for free! '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-V', action='store_true', help='Print version')
    parser.add_argument('-C', action='store', help='Config file',
        default=expanduser('~') + '/.fapi.conf')
    args = vars(parser.parse_args())

    if args['V']:
        print 'This is ' + __program__ + ' version ' + __version__

    fapi = Fapi(args)

    print str(fapi.config)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
