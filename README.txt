NAME
    fapi - A humble command line tool to manage F5 BigIP loadbalancers

    This is a simple command line client to do basic stuff with the iControl
    F5 API such as:

      Managing Nodes
      Managing Monitors
      Managing Pools
      Managing Virtual Servers

Synopsis
    Just run

      fapi -h

    or

      f -h

    because it's shorter to type.

Requirement of bigsuds
    This tool depends on bigsuds. Please install this library from F5 dev
    central manually. Otherwise this script will not work.

    You can download bigsuds from here:

    <https://devcentral.f5.com/d/bigsuds-python-icontrol-library>

    Unzip it and run

      sudo python setyp.py install

iControl reference
    <https://devcentral.f5.com/wiki/icontrol.apireference.ashx>

Project Homepage
    See <http://fapi.buetow.org>

AUTHOR
    Paul C. Buetow - <paul@buetow.org>

