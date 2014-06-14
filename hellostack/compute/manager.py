# -*- coding: utf-8 -*-

import logging
import os.path
from pprint import pprint as pp

import salt.client
import salt.config

from hellostack.compute.db import Flavor, get_session

log = logging.getLogger(__name__)


class ImageService(object):
    """Image Service simply on top of salt file server"""

    def __init__(self, backend='file_roots'):

        opts = salt.config.master_config('/etc/salt/master')
        self.caller = salt.client.Caller()

        # handle different storage backend
        self.top_dir = opts['file_roots']['base'][0]

    def _is_image(self, filepath):
        '''Check whether this file is qemu image'''

        # TODO: check qemu image
        if filepath.endswith('.img'):
            return True
        return False

    def list_image(self, image=None):

        ret = self.caller.function('cp.list_master')
        print "filename      size(KB)"
        for filename in ret:
            file_path = os.path.join(self.top_dir, filename)
            if self._is_image(file_path):
                stat = self.caller.function('file.lstat', file_path)
                if stat:
                    print "%-10s %-6s" % (filename, stat['st_size'])

        return

    def create_image(self):
        pass

    def update_image(self):
        pass

    def delete_image(self, image):
        pass


class FlavorService(object):

    def __init__(self):
        self.db = get_session()

    def list(self, name=None):

        flavors = []
        if name:
            flavors = self.db.query(Flavor).filter_by(
                name=str(name)).first()
        else:
            flavors = self.db.query(Flavor).all()

        if len(flavors):
            print "id  name   vcpu   ram(MB)  disk(GB)"

        for item in flavors:
            print("%-4s %-10s %-4s %-4s %-4s" % (
                item.id, item.name, item.vcpu, item.ram, item.disk))

    def create(self, name, vcpu, ram, disk):

        new = Flavor(name=name, vcpu=vcpu, ram=ram, disk=disk)
        self.db.add(new)
        self.db.commit()

    def update(self):
        pass

    def delete(self, id):

        old = self.db.query(Flavor).filter_by(id=id).first()

        self.db.delete(old)
        self.db.commit()


class Manager(object):
    """Interface for VM"""

    def list_vm(self, vm=None):
        raise NotImplementedError()

    def create_vm(self):
        raise NotImplementedError()

    def update_vm(self):
        raise NotImplementedError()

    def delete_vm(self, vm):
        raise NotImplementedError()


class LibvirtManager(Manager):
    """Compute Service Manager using libvirt API"""

    def __init__(self):

        super(LibvirtManager, self).__init__()

        self.local = salt.client.LocalClient()
        self.caller = salt.client.Caller()

    def call(self, func, *args, **kwargs):
        '''fall into salt module function'''

        # TODO: check salt minion is running
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

    def create_vm(self, name, flavor):

        success = self.call('virt.init', name, flavor.cpu, flavor.raw)
        if success:
            log.debug("create vm:{0} success from flavor:{1}".format(
                name, flavor.name)
            )

        return success

    def update_vm(self):
        raise NotImplementedError()

    def delete_vm(self, vm):
        raise NotImplementedError()


class VmwareManager(Manager):
    """Compute Service Manager for Vmware hypervior """
    pass
