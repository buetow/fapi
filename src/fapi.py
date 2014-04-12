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

        self._config = config
        self._args = args

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
            self._partition = config.get('fapi', 'partition')
            if args.v: print 'Setting partition to %s' % self._partition
            self._f5.Management.Partition.set_active_partition(self._partition)

        except Exception, e:
            print e


    def __login(self, username, password):
        ''' Logs into the F5 BigIP SOAP API '''

        if self._args.v: print 'Login to BigIP API with user %s' % username
        hostname = self._config.get('fapi', 'hostname')

        try:
            self._f5 = bigsuds.BIGIP(
                hostname = hostname,
                username = username,
                password = password,
                )
        except Exception, e:
            print e


    def run(self):
        ''' Do the actual stuff '''

        if self._args.v: print 'Do fancy stuff now'

        f = self._f5
        a = self._args
        flag = False

        if a.action == 'show':
            if a.arg == 'pools':
                print f.LocalLB.Pool.get_list()
                flag = True

            elif a.arg == 'poolstatus':
                pool_name = args.subarg
                print f.LocalLB.Pool.get_object_status([pool_name])
                flag = True

        if not flag: print 'Don\'t know what to do'

if __name__ == '__main__':
    ''' The main function, here we will have Popcorn for free! '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-V', action='store_true', help='Print version')
    parser.add_argument('-C', action='store', help='Config file',
        default=expanduser('~') + '/.fapi.conf')

    parser.add_argument('action', help='The action')
    parser.add_argument('arg', help='The argument for the action')
    parser.add_argument('subarg', nargs='?', help='A sub argument')

    args = parser.parse_args()

    if args.V:
        print 'This is ' + __program__ + ' version ' + __version__
        sys.exit(0)

    fapi = Fapi(args)
    fapi.run()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
