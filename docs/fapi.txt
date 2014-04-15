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

bigsuds
  Requirement of bigsuds
    This tool depends on bigsuds. Please install this library from F5 dev
    central manually. Otherwise this script will not work.

    You can download bigsuds from here:

    <https://devcentral.f5.com/d/bigsuds-python-icontrol-library>

    Unzip it and run

      sudo python setyp.py install

  iControl reference
    Through bigsuds you can do everything what iControl can do:

    <https://devcentral.f5.com/wiki/icontrol.apireference.ashx>

Quick start
  Installing
    Update your sources list:

      curl http://deb.buetow.org/apt/pubkey.gpg | sudo apt-key add -
      echo 'deb http://deb.buetow.org/apt wheezy main' > \
        /etc/apt/sourcees.list.d/buetoworg.list
      aptitude update

    And run

      aptitude install fapi
      cp /usr/share/fapi/fapi.conf.sample ~/.fapi.conf
      vim ~/.fapi.conf

AUTHOR
    Paul C. Buetow - <paul@buetow.org>

    Also see <http://fapi.buetow.org>

