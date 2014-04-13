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


    def out(self, result):
        ''' Prints an iControl result to stdout '''

        if result != None:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)


    #def __help(self, *possible):
    #    ''' Prints an online help '''

    #    print 'Possible sub commands are:'
    #    print ' '.join(possible)


    def lookup(self, what):
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

        if not a.name:
            return lambda: f5().get_list()

        if a.arg == 'get':
            if a.arg2 == 'detail':
                def detail(f5):
                    d = {}
                    d['connection_limit'] = f5().get_connection_limit([a.name])
                    d['default_node_monitor'] = f5().get_default_node_monitor()
                    d['description'] = f5().get_description([a.name])
                    d['dynamic_ratio'] = f5().get_dynamic_ratio_v2([a.name])
                    d['monitor_instance'] = f5().get_monitor_instance([a.name])
                    d['monitor_rule'] = f5().get_monitor_rule([a.name])
                    d['monitor_status'] = f5().get_monitor_status([a.name])
                    d['object_status'] = f5().get_object_status([a.name])
                    d['rate_limit'] = f5().get_rate_limit([a.name])
                    d['ratio'] = f5().get_ratio([a.name])
                    d['session_status'] = f5().get_session_status([a.name])
                    return d
                return lambda: detail(f5)
            if a.arg2 == 'status':
                return lambda: f5().get_monitor_status([a.name])

        elif a.arg == 'create':
                try:
                    data = socket.gethostbyname_ex(a.name)
                except Exception, e:
                    self.info('Can\'t resolve \'%s\': %s' % (a.name, e))
                    sys.exit(2)
                fqdn, ip, _ = self.lookup(a.name)
                return lambda: f5().create([fqdn],[ip],[0])

        elif a.arg == 'delete':
                return lambda: f5().delete_node_address([a.name])


    def __do_monitor(self, f5):
        ''' Do stuff concerning monitor templates '''

        a = self._args

        if not a.name:
            return lambda: f5().get_template_list()

        if a.arg == 'get':
            monitorname = a.arg3
            if a.arg2 == 'desc':
                return lambda: f5().get_description([monitorname])
            if a.arg2 == 'state':
                return lambda: f5().get_template_state([monitorname])


    def __do_pool(self, f5):
        ''' Do stuff concerning pools '''

        a = self._args

        if not a.name:
            return lambda: f5().get_list()

        if a.arg == 'get':
            if a.arg2 == 'detail':
                def detail(f5):
                    d = {}
                    d['allow_nat_state'] = f5().get_allow_nat_state([a.name])
                    d['allow_snat_state'] = f5().get_allow_snat_state([a.name])
                    d['description'] = f5().get_description([a.name])
                    d['lb_method'] = f5().get_lb_method([a.name])
                    d['member'] = f5().get_member_v2([a.name])
                    d['object_status'] = f5().get_object_status([a.name])
                    d['profile'] = f5().get_profile([a.name])
                    return d
                return lambda: detail(f5)
            elif a.arg2 == 'monitor':
                return lambda: f5().get_monitor_instance([a.name])
            elif a.arg2 == 'status':
                return lambda: f5().get_object_status([a.name])
            elif a.arg2 == 'members':
                return lambda: f5().get_member_v2([a.name])

        elif a.arg == 'create':
                poolmembers = []
                method = a.m
                if a.arg3:
                    for x in a.arg3.split(','):
                        fqdn, ip, port = self.lookup(x)
                        pm = { 'address' : fqdn, 'port' : port }
                        poolmembers.append(pm)
                return lambda: f5().create_v2([a.name],[method],[poolmembers])

        elif a.arg == 'delete':
            return lambda: f5().delete_pool([a.name])

        elif a.arg == 'add':
            if a.arg2 == 'member':
                fqdn, _, port = self.lookup(a.arg3)
                member = [{ 'address' : fqdn, 'port' : port }]
                return lambda: f5().add_member_v2([a.name], [member])
            elif a.arg2 == 'monitor':
                monitorname = a.arg3
                rule = {
                    'type': 'MONITOR_RULE_TYPE_SINGLE',
                    'quorum': long(0),
                    'monitor_templates': [ monitorname ],
                }
                association = { 'pool_name': a.name, 'monitor_rule': rule }
                return lambda: f5().set_monitor_association([association])

        elif a.arg == 'del':
            if a.arg2 == 'member':
                fqdn, _, port = self.lookup(a.arg3)
                member = [{ 'address' : fqdn, 'port' : port }]
                return lambda: f5().remove_member_v2([a.name], [member])
            elif a.arg2 == 'monitors':
                # Removes all monitor associations, not just one
                return lambda: f5().remove_monitor_association([a.name])


    def __do_vserver(self, f5):
        ''' Do stuff concerning virtual servers '''

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
        elif a.what == 'vserver':
            lazy = self.__do_vserver(lambda: self._f5.LocalLB.VirtualServer)

        if isfunction(lazy):
            self.__login()
            self.out(lazy())
        else:
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
    parser.add_argument('name', nargs='?', help='The object name to operate on')
    parser.add_argument('arg', nargs='?', help='The first argument')
    parser.add_argument('arg2', nargs='?', help='The second argument')
    parser.add_argument('arg3', nargs='?', help='The third argument')
    #parser.add_argument('arg4', nargs='?', help='The fourth argument')

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
