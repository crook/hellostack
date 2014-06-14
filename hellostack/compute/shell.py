# -*- coding: utf-8 -*-

import time
import sys
from argparse import ArgumentParser

import salt.log
import salt.master
import salt.config
from salt.utils.network import host_to_ip, get_fqhostname

from hellostack.exceptions import *
from hellostack.compute.manager import LibvirtManager
from hellostack.compute.manager import ImageService
from hellostack.compute.manager import FlavorService

log = salt.log.setup.getLogger(__name__)


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
        'help', 'image', 'flavor', 'syncdb',
        'vm', 'net', 'stor',
    ]

    # create/read/update/delete map
    CRUD_MAP = {
        1: 'create',
        2: 'update',
        3: 'delete',
        4: 'list',
        5: 'error',
    }

    def __init__(self, parser):
        self.parser = parser

        log.debug("TODO: load more manager here")
        self.manager = LibvirtManager()
        self.image = ImageService()
        self.flavor = FlavorService()

    def exec_command(self):
        """dispatch command"""

        if not isinstance(self.parser, ArgumentParser):
            raise InvalidParam("Not parser found")

        self.args = self.parser.parse_args()
        print self.args
        salt.log.set_logger_level(__name__, self.args.log_level)
        log.debug("command argument: %r" % self.args)

        if self.args.opt not in self.support_commands:
            raise InvalidParam("Not support sub-command, see help")

        # dispatch command
        try:
            func = getattr(self, "do_%s" % self.args.opt)
            func()
        except Exception as err:
            log.error('call sub-command:{0} failed: {1!r}'.format(
                self.args.opt, err)
            )
            raise RunTimeFailture("call do_func failture")

    def do_syncdb(self):
        pass

    def do_image(self):
        try:
            name = "{0}_image".format(self.CRUD_MAP[self.args.mode])
            function = getattr(self.image, name)
            function()
        except Exception as err:
            log.error('call function{0} failed: {1!r}'.format(
                name, err)
            )
            raise RunTimeFailture("call do_image failure")

    def do_vm(self):
        mode = self.args.mode
        if mode == 1:
            self.manager.create_vm(favor)
        elif mode == 2:
            self.manager.update_vm()
        elif mode == 3:
            self.manager.delete_vm(vm=self.args.name)
        elif mode == 4:
            self.manager.list_vm(vm=self.args.name)
        else:
            raise InvalidParam("Unknown vm mode")

    def do_flavor(self):
        mode = self.args.mode
        if mode == 1:
            self.flavor.create(
                self.args.name, self.args.vcpu,
                self.args.ram, self.args.disk
            )
        elif mode == 2:
            self.flavor.update()
        elif mode == 3:
            self.flavor.delete(vm=self.args.name)
        elif mode == 4:
            self.flavor.list(name=self.args.name)
        else:
            raise InvalidParam("Unknown vm mode")

    def do_net(self):
        pass

    def do_stor(self):
        pass


def option_parser():

    name = sys.argv[0]
    usage = """
    HelloStack Compute Service Shell
    %s sub-command [options] [args]""" % (name)

    parser = ArgumentParser(usage=usage)

    parser.add_argument('--version', action='version', version="1.0")
    parser.add_argument('-n', '--name', dest='name', help="object name")
    parser.add_argument('-i', '--id', dest='id', help="object ID")
    parser.add_argument("-c", "--create", action="store_const",
                        const=1, dest="mode", help="create object")
    parser.add_argument("-e", "--edit", action="store_const",
                        const=2, dest="mode", help="update object")
    parser.add_argument("-d", "--delete", action="store_const",
                        const=3, dest="mode", help="delete object")
    parser.add_argument("-l", "--list", action="store_const",
                        const=4, dest="mode", help="list one/all object")

    parser.add_argument(
        "--log-level", default="info",
        choices=salt.log.LOG_LEVELS.keys(),
        help='Console log level. One of %s. For the logfile settings '
             'see the config file. Default: info' %
             ', '.join([repr(l) for l in salt.log.LOG_LEVELS.keys()]))

    # import sub command group
    subcommands = parser.add_subparsers(dest='opt',
                                        title="available sub-commands")
    vm_command = subcommands.add_parser('vm', help="VM operation")
    image_command = subcommands.add_parser('image', help="Image operation")

    favor_command = subcommands.add_parser('flavor', help="Flavor operation")
    favor_command.add_argument("vcpu", help="Number of vcpus")
    favor_command.add_argument("ram", help="Memory size in MB")
    favor_command.add_argument("disk", help="Disk size in GB")

    net_command = subcommands.add_parser('net', help="Network operation")
    stor_command = subcommands.add_parser('stor', help="Storage operation")

    return parser


def main():
    """
    Start computer service.

    .. code-block:: bash

        hs-computer --server|--node|--all
    """

    salt.log.setup_console_logger()

    parser = option_parser()
    shell = Shell(parser)

    try:
        shell.exec_command()
    except Exception as err:
        log.error("shell command failed: {0!r}".format(
            err)
        )
    except KeyboardInterrupt:
        raise SystemExit('\nExiting gracefully on Ctrl-c')
    finally:
        # TODO: need cleanup
        log.trace("TODO cleanup work")

    return


if __name__ == "__main__":
    main()
