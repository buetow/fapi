#!/usr/bin/env python

# 2014 (c) Paul C. Buetow

import argparse
import base64
import bigsuds
import getpass 
import socket
import sys

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
        self.__login()


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


    def __out(self, message):
        ''' Prints an iControl result to stdout '''
        print message
        #print "\n".join(message)


    def __nslookup(self, what):
        ''' Does a DNS lookup to fetch the FQDN and all the IPs '''
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

        return (fqdn, ips[0])

    def __run_node(self):
        ''' Do stuff concerning nodes '''

        n = self._f5.LocalLB.NodeAddressV2
        a = self._args

        if a.arg == 'show':
            if a.arg2 == 'status':
                self.info('Getting node monitor status of \'%s\'' % nodename)
                nodename = a.arg3
                self.__out(n.get_monitor_status([nodename]))
            elif a.arg2 == 'all':
                self.info('Getting node list')
                self.__out(n.get_list())

        elif a.arg == 'create':
                nodename = a.arg2

                try:
                    data = socket.gethostbyname_ex(nodename)
                except Exception, e:
                    self.info('Can\'t resolve \'%s\': %s' % (nodename, e))
                    sys.exit(2)

                nodefqdn, nodeip = self.__nslookup(nodename)
                self.info('Creating node \'%s\' \'%s\'' % (nodefqdn, nodeip))
                n.create([nodefqdn],[nodeip],[0])

        elif a.arg == 'delete':
                nodename = a.arg2
                self.info('Deleting node \'%s\'' % (nodename))
                n.delete_node_address([nodename])


    def __run_pool(self):
        ''' Do stuff concerning pools '''

        p = self._f5.LocalLB.Pool
        a = self._args

        poolname = a.arg2

        if a.arg == 'show':
            if a.arg2 == 'status':
                self.info('Getting pool status of \'%s\'' % poolname)
                self.__out(p.get_object_status([poolname]))
            elif a.arg2 == 'members':
                self.info('Get pool members of \'%s\'' % poolname)
                self.__out(p.get_member_v2([poolname]))
            elif a.arg2 == 'all':
                self.info('Get pool list')
                self.__out(p.get_list())

        elif a.arg == 'create':
                poolmembers = []
                method = a.m
                if a.arg3:
                    for x in a.arg3.split(','):
                        pm = {}
                        tmp = x.split(':')
                        fqdn, ip = self.__nslookup(tmp[0])
                        if 1 == len(tmp): tmp.append(80)
                        pm['address'] = fqdn
                        pm['port'] = int(tmp[1])
                        poolmembers.append(pm)
                self.info('Creating pool \'%s\'' % poolname)
                p.create_v2([poolname],[method],[poolmembers])

        elif a.arg == 'delete':
            self.info('Deleting pool \'%s\'' % poolname)
            p.delete_pool([poolname])

        elif a.arg == 'addmember':
            tmp = a.arg3.split(':')
            if 1 == len(tmp): tmp.append('80')
            fqdn, ip = self.__nslookup(tmp[0])
            port = tmp[1]

            self.info('Add member \'%s:%s\' to pool \'%s\'' 
                    % (fqdn, port, poolname))
            member = [{ 'address' : fqdn, 'port' : port }]
            p.add_member_v2([poolname], [member])


    def __run_service(self):
        ''' Do stuff concerning virtual services '''

        f = self._f5
        a = self._args


    def run(self):
        ''' Do the actual stuff '''

        if self._args.action == 'node': return self.__run_node()
        elif self._args.action == 'pool': return self.__run_pool()
        elif self._args.action == 'service': return self.__run_service()


if __name__ == '__main__':
    ''' The main function, here we will have Popcorn for free! '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-V', action='store_true', help='Print version')
    parser.add_argument('-m', action='store', help='The lb method',
        default='LB_METHOD_RATIO_LEAST_CONNECTION_MEMBER')
    parser.add_argument('-C', action='store', help='Config file',
        default=expanduser('~') + '/.fapi.conf')

    parser.add_argument('action', nargs='?', help='The action')
    parser.add_argument('arg', nargs='?', help='The argument for the action')
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
