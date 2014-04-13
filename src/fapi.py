#!/usr/bin/env python

# 2014 (c) Paul C. Buetow

import argparse
import base64
import bigsuds
import getpass 
import pprint
import socket
import sys

from os.path import expanduser
from inspect import isfunction

import ConfigParser

__program__ = 'fapi'
__version__ = 'VERSION_DEVEL' # Replaced by a Makefile target
__prompt__  = '>>>' # Default prompt

class Fapi(object):
    ''' The main F5 API Tool Object '''

    def __init__(self, args):
        ''' Initialize the config file, username and password '''

        self._config = ConfigParser.ConfigParser()
        self._config.read(args.C)
        self._args = args


    def __login(self):
        ''' Logs into the F5 BigIP SOAP API and changes the partition'''

        c = self._config

        if c.has_option('fapi', 'username'):
            username = c.get('fapi', 'username')
        else:
            username = getpass.getuser()

        if c.has_option('fapi', 'password64'):
            password = base64.decodestring(c.get('fapi', 'password64'))
        else:
            prompt = 'Enter API password for user %s: ' % username
            password = getpass.getpass(prompt)

        self.info('Login to BigIP API with user %s' % username)
        hostname = c.get('fapi', 'hostname')

        # Enhance to try to login to a list of hosts
        try:
            self._f5 = bigsuds.BIGIP(hostname = hostname,
                                     username = username,
                                     password = password)
            self._partition = c.get('fapi', 'partition')
            self.info('Setting partition to \'%s\'' % self._partition)
            self._f5.Management.Partition.set_active_partition(self._partition)
        except Exception, e:
            self.info(e)
            sys.exit(2)


    def info(self, message):
        ''' Prints an informational message to stderr '''
        
        print >> sys.stderr, '%s %s' % (__prompt__, message)


    def __out(self, result):
        ''' Prints an iControl result to stdout '''

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)


    def __lookup(self, what):
        ''' Does a DNS lookup to fetch the FQDN and all the IPs '''

        tmp = what.split(':')
        if 1 == len(tmp): tmp.append('80')
        what = tmp[0]
        port = tmp[1]
        try:
            data = socket.gethostbyname_ex(what)
        except Exception, e:
            self.info('Can\'t resolve \'%s\': %s' % (what, e))
            sys.exit(2)
        fqdn = data[0]
        ips = data[2]
        if len(ips) > 1:
            self.info('\'%s\' resolves to multiple ips \'%s\'' % (fqdn, ips))
            sys.exit(2)
        return (fqdn, ips[0], port)

    def __do_node(self, f5):
        ''' Do stuff concerning nodes '''

        a = self._args

        if a.arg == 'show':
            if a.arg2 == 'detail':
                nodename = a.arg3
                def monitor_status(f5):
                    d = {}
                    d['connection_limit'] = f5().get_connection_limit([nodename])
                    d['default_node_monitor'] = f5().get_default_node_monitor()
                    d['description'] = f5().get_description([nodename])
                    d['dynamic_ratio'] = f5().get_dynamic_ratio_v2([nodename])
                    d['monitor_instance'] = f5().get_monitor_instance([nodename])
                    d['monitor_rule'] = f5().get_monitor_rule([nodename])
                    d['monitor_status'] = f5().get_monitor_status([nodename])
                    d['object_status'] = f5().get_object_status([nodename])
                    d['rate_limit'] = f5().get_rate_limit([nodename])
                    d['ratio'] = f5().get_ratio([nodename])
                    d['session_status'] = f5().get_session_status([nodename])
                    return d
                return lambda: monitor_status(f5)
            elif a.arg2 == 'all':
                return lambda: f5().get_list()

        elif a.arg == 'create':
                nodename = a.arg2
                try:
                    data = socket.gethostbyname_ex(nodename)
                except Exception, e:
                    self.info('Can\'t resolve \'%s\': %s' % (nodename, e))
                    sys.exit(2)
                fqdn, ip, _ = self.__lookup(nodename)
                return lambda: f5().create([fqdn],[ip],[0])

        elif a.arg == 'delete':
                nodename = a.arg2
                return lambda: f5().delete_node_address([nodename])


    def __do_monitor(self, f5):
        ''' Do stuff concerning monitor templates '''

        a = self._args

        if a.arg == 'show':
            monitorname = a.arg3
            if a.arg2 == 'desc':
                return lambda: f5().get_description([monitorname])
            if a.arg2 == 'state':
                return lambda: f5().get_template_state([monitorname])
            elif a.arg2 == 'all':
                return lambda: f5().get_template_list()


    def __do_pool(self, f5):
        ''' Do stuff concerning pools '''

        a = self._args
        poolname = a.arg2

        if a.arg == 'show':
            if a.arg2 == 'status':
                return lambda: f5().get_object_status([poolname])
            elif a.arg2 == 'members':
                return lambda: f5().get_member_v2([poolname])
            elif a.arg2 == 'all':
                return lambda: f5().get_list()

        elif a.arg == 'create':
                poolmembers = []
                method = a.m
                if a.arg3:
                    for x in a.arg3.split(','):
                        fqdn, ip, port = self.__lookup(x)
                        pm = { 'address' : fqdn, 'port' : port }
                        poolmembers.append(pm)
                return lambda: f5().create_v2([poolname],[method],[poolmembers])

        elif a.arg == 'delete':
            return lambda: f5().delete_pool([poolname])

        elif a.arg == 'add':
            fqdn, _, port = self.__lookup(a.arg3)
            member = [{ 'address' : fqdn, 'port' : port }]
            return lambda: f5().add_member_v2([poolname], [member])

        elif a.arg == 'remove':
            fqdn, _, port = self.__lookup(a.arg3)
            member = [{ 'address' : fqdn, 'port' : port }]
            return lambda: f5().remove_member_v2([poolname], [member])


    def __do_service(self, f5):
        ''' Do stuff concerning virtual services '''

        a = self._args


    def run(self):
        ''' Do the actual stuff.
            We are doning some lazy evaluation stuff here. The command line
            tool does not do anything with the slow F5 API until it is clear
            what to do and that there is no semantic or syntax error. '''

        a = self._args
        lazy = None

        if a.what == 'node':
            lazy = self.__do_node(lambda: self._f5.LocalLB.NodeAddressV2)
        elif a.what == 'monitor':
            lazy = self.__do_monitor(lambda: self._f5.LocalLB.Monitor)
        elif a.what == 'pool':
            lazy = self.__do_pool(lambda: self._f5.LocalLB.Pool)
        elif a.what == 'service':
            lazy = self.__do_service(lambda: self._f5)

        if isfunction(lazy):
            self.__login()
            self.__out(lazy())
        else:
            self.info('Don\t know what to do')
            sys.exit(1)


if __name__ == '__main__':
    ''' The main function, here we will have Popcorn for free! '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-V', action='store_true', help='Print version')
    parser.add_argument('-m', action='store', help='The lb method',
        default='LB_METHOD_RATIO_LEAST_CONNECTION_MEMBER')
    parser.add_argument('-C', action='store', help='Config file',
        default=expanduser('~') + '/.fapi.conf')

    parser.add_argument('what', nargs='?', help='What')
    parser.add_argument('arg', nargs='?', help='The argument for what')
    parser.add_argument('arg2', nargs='?', help='A sub argument')
    parser.add_argument('arg3', nargs='?', help='Another sub argument')

    args = parser.parse_args()

    if args.V:
        print 'This is %s version %s' % (__program__, __version__)
        sys.exit(0)

    fapi = Fapi(args)

    fapi.run()

#   try: 
#       if not fapi.run():
#           fapi.info('Don\'t know what to do')
#           sys.exit(1)
#   except Exception, e:
#       fapi.info(e)
#       sys.exit(2)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
