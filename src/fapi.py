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
__prompt__  = '>>>' # Default prompt

class Fapi(object):
    ''' The main F5 API Tool Object '''

    def __init__(self, args):
        ''' Initialize the config file, username and password '''

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
            self.info('Setting partition to %s' % self._partition)

            self._f5.Management.Partition.set_active_partition(self._partition)

        except Exception, e:
            self.info(e)
            sys.exit(2)


    def __login(self, username, password):
        ''' Logs into the F5 BigIP SOAP API '''

        self.info('Login to BigIP API with user %s' % username)
        hostname = self._config.get('fapi', 'hostname')

        # Enhance to try to login to a list of hosts
        try:
            self._f5 = bigsuds.BIGIP(
                hostname = hostname,
                username = username,
                password = password,
                )
        except Exception, e:
            self.info(e)
            sys.exit(2)


    def info(self, message):
        ''' Prints an informational message to stderr '''
        print >> sys.stderr, '%s %s' % (__prompt__, message)


    def __run_pool(self):
        ''' Do stuff concerning pools '''

        f = self._f5
        a = self._args

        if a.arg == 'show':
            if a.subarg == 'status':
                self.info('Getting pool status')
                poolname = a.subarg2
                print f.LocalLB.Pool.get_object_status([poolname])
                return True

            elif a.subarg == 'members':
                self.info('Get pool members')
                poolname = a.subarg2
                print f.LocalLB.Pool.get_member_v2([poolname])
                return True

            else:
                self.info('Get pool list')
                print f.LocalLB.Pool.get_list()
                return True

        elif a.arg == 'create':
                poolname = a.subarg
                poolmembers = []
                method = a.m
                if a.subarg2:
                    for x in a.subarg2.split(','):
                        pm = {}
                        y = x.split(':')
                        if 1 == len(y): y.append(80)
                        pm['address'] = str(y[0])
                        pm['port'] = int(y[1])
                        poolmembers.append(pm)
                f.LocalLB.Pool.create_v2([poolname],[method],[poolmembers])
                return True

        return False


    def __run_service(self):
        ''' Do stuff concerning virtual services '''

        f = self._f5
        a = self._args

        return False


    def run(self):
        ''' Do the actual stuff '''

        flag = False
        a = self._args

        if a.action == 'pool':
            flag = self.__run_pool()

        elif a.action == 'service':
            flag = self.__run_service()

        if not flag: 
            self.info('Don\'t know what to do')
            sys.exit(1)



if __name__ == '__main__':
    ''' The main function, here we will have Popcorn for free! '''

    parser = argparse.ArgumentParser()
    #parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-V', action='store_true', help='Print version')
    parser.add_argument('-m', action='store', help='The lb method',
        default='LB_METHOD_RATIO_LEAST_CONNECTION_MEMBER')
    parser.add_argument('-C', action='store', help='Config file',
        default=expanduser('~') + '/.fapi.conf')

    parser.add_argument('action', help='The action')
    parser.add_argument('arg', help='The argument for the action')
    parser.add_argument('subarg', nargs='?', help='A sub argument')
    parser.add_argument('subarg2', nargs='?', help='Another sub argument')

    args = parser.parse_args()

    fapi = Fapi(args)

    if args.V:
        print 'This is %s version %s' % (__program__, __version__)
        sys.exit(0)

    #try: 
    fapi.run()
    #except Exception, e:
    #    fapi.info(e)
    #    sys.exit(2)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
