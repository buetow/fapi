NAME
    fapi - A humble command line tool to manage F5 BigIP loadbalancers

SYNOPSIS
    Just run

      fapi -h

    or

      f -h

    because it's shorter to type.

ABOUT
    This is a simple command line client to do basic stuff with the iControl
    F5 API such as:

      Managing Nodes
      Managing Monitors
      Managing Pools
      Managing Virtual Servers

    This is a private programming project programmed in my spare time.
    Therefore I didn't bother to put it on a public website and github.
    Please open bug reports, feature requests and pull requests at
    <https://github.com/rantanplan/fapi>.

BIGSUDS
  Requirement of bigsuds
    This tool depends on bigsuds. Please install this library from F5 dev
    central manually. Otherwise this script will not work.

    You can download bigsuds from here:

    <https://devcentral.f5.com/d/bigsuds-python-icontrol-library>

    Unzip it and run

      sudo python setyp.py install

    You may also install bigsuds from the contrib dir of the fapi source
    tree.

  iControl reference
    Through bigsuds you can do everything what iControl can do:

    <https://devcentral.f5.com/wiki/icontrol.apireference.ashx>

QUICK START
    Update your sources list:

      curl http://deb.buetow.org/apt/pubkey.gpg | sudo apt-key add -
      echo 'deb http://deb.buetow.org/apt wheezy main' > \
        /etc/apt/sourcees.list.d/buetoworg.list
      aptitude update

    And run

      aptitude install fapi
      cp /usr/share/fapi/fapi.conf.sample ~/.fapi.conf
      vim ~/.fapi.conf

EXAMPLES
  Setting up simple NAT Services
      (Docu to be written)

  Setting up simple SNAT Services
      (Docu to be written)

  Setting up a simple nPath Service
    A simple nPath service can be created as follows.

      # Creating two nodes, auto resolve the IP addresses
      f node fooserver1.example.com create
      f node fooserver2.example.com create

      # Creating a pool and add the nodes to it
      f pool foopool create
      f pool foopool add member fooserver1.example.com:80
      f pool foopool add member fooserver2.example.com:80

      # Add a monitor to the pool
      f pool foopool add monitor http_lbtest

      # Create a nPath HTTP service, 'nPath' also auto disables NAT and PAT
      f vserver myservice.example.com:80 create PROTOCOL_TCP nPath

      # Add the pool to the service
      f vserver myservice.example.com:80 set pool foopool

      # Add a nPath HTTPS service
      f vserver myservice.example.com:443 create PROTOCOL_TCP nPath
      f vserver myservice.example.com:443 set pool foopool

AUTHOR
    Paul C. Buetow - <paul@buetow.org>

    Also see <http://fapi.buetow.org>

