# -*- coding: utf-8 -*-

import logging
import time
import sys
from optparse import OptionParser

import salt.master
import salt.config
from salt.utils.network import host_to_ip, get_fqhostname

from hellostack.exceptions import *
from hellostack.compute.manager import libvirtManager
from hellostack.utils import setup_logger

log = logging.getLogger(__name__)


def launch_all():
    launch_server()
    launch_node()


def launch_server():
    """
    Start the salt master here
    """

    hostname = get_fqhostname()
    ip = host_to_ip(hostname)
    log.debug("Hellostack start server %s" % ip)

    master_opts = salt.config.client_config("/etc/salt/master")
    master = salt.master.Master(master_opts)
    master.start()


def launch_node():
    """
    Start the salt minion here
    """
    reconnect = True
    while reconnect:
        reconnect = False
        minion = salt.Minion()
        ret = minion.start()
        if ret == 'reconnect':
            del minion
            minion = None
            time.sleep(10)
            reconnect = True


class Shell(object):
    """Shell command"""

    support_commands = [
        'help', 'image', 'favor', 'syncdb',
        'vm', 'net', 'stor',
    ]

    def __init__(self, parser):
        self.parser = parser

        log.debug("TODO: load more manager here")
        self.manager = libvirtManager()

    def exec_command(self):
        """dispatch command"""

        if not isinstance(self.parser, OptionParser):
            raise InvalidParam("Not parser found")

        (options, args) = self.parser.parse_args()
        self.mode = options.mode

        # default print help message
        subcommand = 'help'
        if len(args):
            subcommand = args[0]

        if subcommand not in self.support_commands:
            raise InvalidParam("Not support sub-command, see help")

        # dispatch command
        try:
            func = getattr(self, "do_%s" %subcommand)
            func()
        except Exception as err:
            log.error('call subcommand:{0} failed: {1}'.format(
                subcommand, err)
            )
            print err
            raise RunTimeFailture("call do_func failture")

    def do_syncdb(self):
        pass

    def do_image(self):
        pass

    def do_vm(self):
        if self.mode == 1:
            self.manager.create_vm()
        elif self.mode == 2:
            self.manager.update_vm()
        elif self.mode == 3:
            self.manager.delete_vm()
        elif self.mode == 4:
            self.manager.list_vm()
        else:
            raise InvalidParam("Unkown vm mode")

    def do_favor(self):
        pass

    def do_net(self):
        pass

    def do_stor(self):
        pass


def option_parser():

    name = sys.argv[0]
    usage="""
    HelloStack Compute Service Shell

    %s subcommand [options] [args]

    Available Sub-commands:
        server
        node
        syncdb
        image
        favor
        vm
        net
        stor

    List of image commands:
        %s image [-c][-d][-l][-e] [args]

        -l|--list    list images
        -c|--create  create one image
        -e|--edit    update one image
        -d|--delete  delete one image""" %(name,name)

    parser = OptionParser(usage=usage)

    parser.add_option("-c", "--create", action="store_const",
                      const=1, dest="mode", help="create object")
    parser.add_option("-e", "--edit", action="store_const",
                      const=2, dest="mode", help="update object")
    parser.add_option("-d", "--delete", action="store_const",
                      const=3, dest="mode", help="delete object")
    parser.add_option("-l", "--list", action="store_const",
                      const=4, dest="mode",help="list one/all object")

    return parser


def main():
    """
    Start computer service.

    .. code-block:: bash

        hs-computer --server|--node|--all
    """

    # setup_logger("computer.log")

    parser = option_parser()
    shell = Shell(parser)

    try:
        shell.exec_command()
    except Exception as err:
        log.debug("shell command failed: {0}".format(
            err)
        )
        print err
    except KeyboardInterrupt:
        raise SystemExit('\nExiting gracefully on Ctrl-c')
    finally:
        # TODO: need cleanup
        log.debug("TODO cleanup work")

    return


if __name__ == "__main__":
    main()
