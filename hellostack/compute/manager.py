# -*- coding: utf-8 -*-

import logging
from pprint import pprint as pp

import salt.client

log = logging.getLogger(__name__)


class Manager(object):
    """Interface for VM"""

    def list_vm(self):
        raise NotImplementedError()

    def create_vm(self):
        raise NotImplementedError()

    def update_vm(self):
        raise NotImplementedError()

    def delete_vm(self):
        raise NotImplementedError()


class libvirtManager(Manager):
    """Compute Service Manager using libvirt API"""

    def __init__(self):

        super(libvirtManager, self).__init__()

        self.local = salt.client.LocalClient()
        self.caller = salt.client.Caller()

    def call(self, func, *args, **kwargs):
        '''fall into salt module function'''

        log.debug("TODO: check salt minion is running")
        return self.caller.sminion.functions[func](*args, **kwargs)

    def _print_vm(self, vmname, vminfo, full=False):
        details = vminfo[vmname]
        print("%-10s %-6s %-8s %-8s" % (vmname,
                                        details['cpu'],
                                        details['mem'],
                                        details['state']))
        # dump details
        if full:
            print "\nVM Details"
            pp(vminfo)

    def list_vm(self, vm=None):

        if vm:
            vminfo = self.call('virt.vm_info', vm)
            print "name      cpu   mem      state"
            self._print_vm(vm, vminfo, full=True)
            return

        # list all vms in system
        self.vms = self.call('virt.list_vms')
        print "name      cpu   mem      state"
        log.debug("TODO: add cache support, otherwise too slow")
        for vmname in self.vms:
            vminfo = self.call('virt.vm_info', vmname)
            self._print_vm(vmname, vminfo)

    def create_vm(self):
        raise NotImplementedError()

    def update_vm(self):
        raise NotImplementedError()

    def delete_vm(self):
        raise NotImplementedError()


class vmwareManager(Manager):
    """Compute Service Manager for Vmware hypervior """
    pass
