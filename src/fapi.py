#!/usr/bin/env python

# 2014 (c) Paul C. Buetow

import argparse
import base64
import getpass 
import sys
import bigsuds

from os.path import expanduser

import ConfigParser

__program__ = 'fapi'
__version__ = 'VERSION_DEVEL' # Replaced by a Makefile target

class Fapi(object):
    ''' The main F5 API Tool Object '''

    def __init__(self, args):
        ''' Initialize the config file, username and password '''

        if args.v:
            print 'Reading configuration'

        config_file = args.C

        config = ConfigParser.ConfigParser()
        config.read(config_file)

        self.config = config
        self.args = args

        if config.has_option('fapi', 'username'):
            username = config.get('fapi', 'username')
        else:
            username = getpass.getuser()

        if config.has_option('fapi', 'password64'):
            password = base64.decodestring(config.get('fapi', 'password64'))
        else:
            prompt = 'Enter API password for user %s: ' % username
            password = getpass.getpass(prompt)

        self.__login(username, password)

        try:
            self.bigip.Management.Partition.set_active_partition(
                config.get('fapi', 'partition'))

        except Exception, e:
            print "Exception: %s" % e


    def __login(self, username, password):
        ''' Logs into the F5 BigIP SOAP API '''

        if args.V:
            print 'Login to BigIP API with user %s' % username

        hostname = self.config.get('fapi', 'hostname')

        try:
            self.bigip = bigsuds.BIGIP(
                hostname = hostname,
                username = username,
                password = password,
                )
        except Exception, e:
            print "Exception: %s" % e

    def run(self):
        ''' Do the actual stuff '''

        if args.list:
            print 'Hello'

        else:
            print 'No such action'

if __name__ == '__main__':
    ''' The main function, here we will have Popcorn for free! '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-V', action='store_true', help='Print version')
    parser.add_argument('-C', action='store', help='Config file',
        default=expanduser('~') + '/.fapi.conf')

    parser.add_argument('list', action='store_false', help='List')
    parser.add_argument('pool', action='store_false', help='Server pool')

    args = parser.parse_args()

    if args.V:
        print 'This is ' + __program__ + ' version ' + __version__
        sys.exit(0)

    print vars(args)

    fapi = Fapi(args)
    fapi.run()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
