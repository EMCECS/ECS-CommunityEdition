# coding=utf-8
# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import os
import string
import random
import logging
from defaults import *

logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)

DEFAULTS = {}

# Top level stuff
# NODE_DEFAULTS = 'node_defaults'
INSTALL_NODE = 'install_node'
MANAGEMENT_CLIENTS = 'management_clients'

_D = '_defaults'
OPTIONS = 'options'
NAME = 'name'
MEMBERS = 'members'
DESC = 'description'
DESC_DEFAULT = 'Default description'

FUN_FACTS = [INSTALL_NODE, MANAGEMENT_CLIENTS]

# Directory Table stuff
DIRECTORY_TABLE = {
    'small': 384,
    'large': 1400
}

# Ansible stuff is a special case where the same password is
# typically used for all three password args. We should wire
# all three to an "ansible_password" meta var.  Individual
# password fields can still be overridden in deploy.yml.
# Wire an "ansible_username" meta var to ansible_user for
# consistency.
# Also, consider implications of ssh pubkey auth.
ANSIBLE_DEFAULTS = 'ssh_defaults'
ANSIBLE_USER = 'ssh_username'
ANSIBLE_PASS = 'ssh_password'
ANSIBLE_PORT = 'ssh_port'
ANSIBLE_PORT_DEFAULT = 22
ANSIBLE_SPECIAL_KEYS = {
    'ansible_user': 'username',
    'ansible_username': 'username',
    'ansible_ssh_pass': 'password',
    'ansible_become_pass': 'password',
    'ansible_port': 'ssh_port'
}
# 'ansible_password': 'password',
ANSIBLE = 'sshs'
ANSIBLE_D = ANSIBLE[:-1] + _D
DEFAULTS[ANSIBLE] = {
    'ssh_username': None,
    'ansible_username': None,
    'ansible_user': None,
    'ssh_password': None,
    'ansible_password': None,
    'ansible_ssh_pass': None,
    'ansible_become_pass': None,
    'ssh_port': ANSIBLE_PORT_DEFAULT,
    'ansible_port': None
}

# Node-level stuff
ROOT_PASS = 'ecs_root_pass'
ROOT_PASS_DEFAULT = 'ChangeMe'
ROOT_USER = 'ecs_root_user'
ROOT_USER_DEFAULT = 'root'
ENTROPY_SOURCE = 'entropy_source'
ENTROPY_SOURCE_DEFAULT = '/dev/urandom'
AUTONAMING = 'autonaming'
AUTONAMING_DEFAULT = 'moons'
NODE = 'nodes'
NODE_D = NODE[:-1] + _D
DEFAULTS[NODE] = {
    ROOT_USER: ROOT_USER_DEFAULT,
    ROOT_PASS: ROOT_PASS_DEFAULT,
    ENTROPY_SOURCE: ENTROPY_SOURCE_DEFAULT,
    AUTONAMING: AUTONAMING_DEFAULT
}

# Storage Pool stuff
SP = 'storage_pools'
SP_D = SP[:-1] + _D
DEFAULTS[SP] = {
    'is_cold_storage_enabled': False,
    'is_protected': False,
    DESC: DESC_DEFAULT
}

# Virtual Datacenter stuff
VDC = 'virtual_data_centers'
VDC_D = VDC[:-1] + '_defaults'
DEFAULTS[VDC] = {}

# Replication Group stuff
RG = 'replication_groups'
RG_D = RG[:-1] + _D
DEFAULTS[RG] = {
    'enable_rebalancing': True,
    'allow_all_namespaces': True,
    'is_full_rep': False,
    DESC: DESC_DEFAULT
}

# Authentication Provider stuff
AUTH = 'auth_providers'
AUTH_D = AUTH[:-1] + _D
DEFAULTS[AUTH] = {
    DESC: DESC_DEFAULT
}

# Namespace stuff
NAMESPACE_ADMINS = 'administrators'
NAMESPACE_ADMINS_DEFAULT = 'root'
NAMESPACE_VPOOL = 'replication_group'
NS = 'namespaces'
NS_D = NS[:-1] + _D
DEFAULTS[NS] = {
    'is_encryption_enabled': False,
    'is_stale_allowed': False,
    'is_compliance_enabled': False,
}

# Management user stuff
MU = 'management_users'
MU_D = MU[:-1] + _D
DEFAULTS[MU] = {
    DESC: DESC_DEFAULT
}

# Object User stuff
OU = 'object_users'
OU_D = OU[:-1] + _D
DEFAULTS[OU] = {
    DESC: DESC_DEFAULT
}

# Bucket stuff
BUCKET = 'buckets'
BUCKET_D = MU[:-1] + _D
DEFAULTS[BUCKET] = {
    DESC: DESC_DEFAULT
}

# File export stuff
EXPORT = 'exports'
EXPORT_D = EXPORT[:-1] + _D
DEFAULTS[EXPORT] = {
    DESC: DESC_DEFAULT
}


class ECSConf(object):
    """
    Provides access to ECS deployment mappings within the given DotMap object
    """

    def __init__(self, deploymap):

        self.deploy = deploymap

    @staticmethod
    def get_dt_total(self, footprint):
        """
        Accessor for directory table data
        :param footprint: small or large
        :return: int
        """
        return DIRECTORY_TABLE[footprint]

    def get_attr(self, map_type, key=None, name=None):
        """
        Access common patterns within the ECSConf object
        """
        try:
            # If only map_type provided, return the data at map_type in the yaml tree
            if key is None and name is None:
                return self.deploy.facts[map_type]
            # If map_type and key are provided, return the data at key of map_type in the yaml tree
            if key is not None and name is None:
                return [x[key] for x in self.deploy.facts[map_type]]
            # If map_type, key, and name are provided, then return the name field at key of
            # map_type in the yaml tree
            if key is not None and name is not None:
                return [x[key] for x in self.deploy.facts[map_type] if x[NAME] == name][0]
        except KeyError:
            return None

    def get_ansible_facts(self):
        """
        Returns a dict of Ansible facts
        :return: dict of facts
        """

        facts = {}
        facts.update(self.get_defaults(ANSIBLE))

        for sk, sv in ANSIBLE_SPECIAL_KEYS.iteritems():
            if facts[sk] is None:
                if sv == 'username':
                    facts[sk] = facts[ANSIBLE_USER]
                elif sv == 'password':
                    facts[sk] = facts[ANSIBLE_PASS]
                elif sv == 'ssh_port':
                    facts[sk] = facts[ANSIBLE_PORT]
                else:
                    # This shouldn't happen
                    raise KeyError("Missing default value for key: ".format(sk))

        return facts

    def get_fun_facts(self):
        """
        Returns a dict of important general facts
        :return: dict of facts
        """
        fun_facts = {}

        for key in FUN_FACTS:
            fun_facts[key] = self.get_attr(key)

        fun_facts.update(self.get_ansible_facts())
        return fun_facts

    def get_names(self, map_type):
        """
        Returns a list of name keys from the given map_type
        """
        return self.get_attr(map_type, NAME)

    def get_members(self, map_type, name, key=MEMBERS):
        """
        Returns a list of items from the members key of the given map_type and name
        """
        return self.get_attr(map_type, key, name)

    def get_root_user(self):
        """
        Returns the configured root user for the ECS deployemnt
        """
        return self.get_node_defaults()[ROOT_USER]

    def get_root_pass(self):
        """
        Returns the configured root password for the ECS deployment
        """
        return self.get_node_defaults()[ROOT_PASS]

    @staticmethod
    def gen_secret(length=20, charset=None):
        """
        Generates a less insecure random string
        By default it is a VDC Secret Key compatible 20-character random string
        :param length: How long do you want it? int
        :param charset: Set of characters from which to choose randomly
        :returns: Random string
        """
        if charset is None:
            charset = '{}{}{}'.format(string.ascii_uppercase, string.ascii_lowercase, string.digits)
        return ''.join(random.SystemRandom().choice(charset) for _ in range(length))

    def get_defaults(self, map_type):
        """
        Returns a dict of default options for the map type
        """
        result = {}
        result.update(DEFAULTS[map_type])
        map_type_d = map_type[:-1] + _D
        # if map_type in self.deploy.facts and map_type_d in self.deploy.facts:
        if map_type_d in self.deploy.facts:
            result.update(self.deploy.facts[map_type_d].toDict())
        return result

# Data Store nodes
    def get_node_pool(self, node):
        """
        Returns the pool name of the pool the node belongs to
        :param node: ansible_hostname of the node
        :returns: pool name or None
        """
        for sp in self.get_sp_names():
            if node in self.get_sp_members(sp):
                return sp
        return None

    def get_node_vdc(self, node):
        """
        Returns the VDC name that the node belongs to
        :param node: ansible_hostname of the node
        :return: vdc name or None
        """
        pool = self.get_node_pool(node)
        for vdc in self.get_vdc_names():
            if pool in self.get_vdc_members(vdc):
                return vdc
        return None

    def get_node_defaults(self):
        """

        :return:
        """
        # opts = {}
        # if NODE_DEFAULTS in self.deploy.facts:
        #     opts.update(self.deploy.facts[NODE_DEFAULTS].toDict())
        return self.get_defaults(NODE)

    def get_node_options(self, node):
        """
        Returns the options dict for the node after resolving variable precedence
        :param node: ansible_hostname of the node
        :returns: dict of node options or blank dict
        """
        opts = {}

        opts.update(self.get_node_defaults())

        if ANSIBLE_DEFAULTS in self.deploy.facts:
            opts.update(self.deploy.facts[ANSIBLE_DEFAULTS].toDict())

        # do stuff if node belongs to a storage pool
        if self.get_node_pool(node) is not None:
            opts.update(self.get_defaults(SP))
            node_pool = self.get_node_pool(node)
            pool_options = self.get_sp_options(node_pool)
            if node_pool is not None and pool_options is not None:
                opts.update(pool_options)

        return opts

    def list_all_nodes(self):
        """
        Returns a list of all nodes of any type in deploy.yml
        :return:
        """
        nodes = [self.deploy.facts[INSTALL_NODE]]
        nodes += self.list_all_sp_nodes()
        return nodes

    def list_all_sp_nodes(self):
        """
        Returns a list of all SP nodes known about in deploy.yml
        """
        nodes = []
        for sp in self.get_sp_names():
            nodes.extend(self.get_sp_members(sp))
        return nodes

    def get_any_endpoint(self):
        """
        Returns a random node from the list of all known nodes
        """
        return random.SystemRandom().choice(self.list_all_sp_nodes())

# Storage Pools
    def get_sp_names(self):
        """
        Returns a list of names of storage pools in deploy.yml
        :returns: List of storage pool names
        """
        return self.get_names(SP)

    def get_sp_members(self, pool_name):
        """
        Returns a list of all nodes in the pool
        :param pool_name: Name of the pool to list membership
        :returns: List of nodes in the pool
        """
        return self.get_members(SP, pool_name)

    def get_sp_options(self, pool_name):
        """
        Returns the options dict for the pool
        :param pool_name: Name of the pool
        :return: dict of pool options
        """
        opts = self.get_defaults(SP)
        sp_opts = self.get_attr(SP, OPTIONS, pool_name).toDict()
        if sp_opts is not None:
            opts.update(sp_opts)
        return opts

    def get_sp_ecs_options(self, pool_name):
        """
        Returns options only pertaining to the storage pool configuration within ECS
        :param pool_name: Name of the pool to report options on
        """
        return {x: y for x, y in self.get_sp_options(pool_name).items() if x in DEFAULTS[SP].keys()}

    def sp_ecs_options(self, pool_name):
        """
        Returns options only pertaining to the storage pool configuration within ECS
        :param pool_name: Name of the pool to report options on
        """
        return {x: y for x, y in self.get_sp_options(pool_name).items() if x in DEFAULTS[SP].keys()}

    # Virtual Data Centers
    def get_vdc_names(self):
        """
        Returns a list of names of all configured VDCs in the deployment
        """
        return self.get_names(VDC)

    def get_vdc_members(self, vdc_name):
        """
        Returns a list of the names of all storage pools assigned to the VDC
        """
        return self.get_members(VDC, vdc_name)

    def get_vdc_endpoint(self, vdc_name):
        return self.get_sp_members(self.get_vdc_members(vdc_name)[0])[0]

    # def get_vdc_endpoint(self, vdc_name):
    #     """
    #     Returns a random node belonging to a storage pool in a specific VDC
    #     """
    #     nodes = []
    #     for sp in self.get_vdc_members(vdc_name):
    #         nodes += self.get_sp_members(sp)
    #     return random.SystemRandom().choice(nodes)

    def get_new_vdc_secret(self, vdc_name):
        """
        Returns the configured VDC secret key, or None if no key is defined for the VDC
        """
        return self.get_attr(VDC, OPTIONS, vdc_name).secret_key

    def get_vdc_options(self, vdc_name):
        """
        Returns the options dict for the vdc
        :param vdc_name: Name of the vdc
        :return: dict of vdc options
        """
        opts = self.get_defaults(VDC)
        vdc_opts = self.get_attr(VDC, OPTIONS, vdc_name)
        if vdc_opts is not None:
            opts.update(vdc_opts)
        return opts

# Replication Groups
    def get_rg_names(self):
        """
        Returns a list of names of all replication groups in the configuration
        """
        return self.get_names(RG)

    def get_rg_members(self, rg_name):
        """
        Returns a list of all VDCs for the given replication group name
        """
        return self.get_members(RG, rg_name)

    def get_rg_options(self, rg_name):
        """
        Returns the options dict for the rg
        :param rg_name: Name of the rg
        :return: dict of rg options
        """
        opts = self.get_defaults(RG)
        rg_opts = self.get_attr(RG, OPTIONS, rg_name)
        if rg_opts is not None:
            opts.update(rg_opts)
        return opts

# Namespaces
    def get_ns_names(self):
        return self.get_names(NS)

    def get_ns_users(self, ns_name):
        users = self.get_members(NS, ns_name, NAMESPACE_ADMINS)[0]
        if users is None:
            users = [NAMESPACE_ADMINS_DEFAULT]
        return users

    def get_ns_options(self, ns_name):
        """
        Returns the options dict for the rg
        :param rg_name: Name of the rg
        :return: dict of rg options
        """
        opts = self.get_defaults(NS)
        ns_opts = self.get_attr(NS, OPTIONS, ns_name)
        if ns_opts is not None:
            opts.update(ns_opts)
        return opts

    def get_ns_vpool(self, ns_name):
        """
        returns the default vpool of the named namespace
        :param ns_name: ns name
        :return:
        """
        return self.get_attr(NS, NAMESPACE_VPOOL, ns_name)

    def get_ns_dict(self, ns_name):
        """
        returns dict describing the named namespace
        :param ns_name:
        :return: ns_dict
        """
        ns_dict = {}
        ns_dict.update(self.get_ns_options(ns_name))
        ns_dict.update({NAMESPACE_ADMINS: self.get_ns_users(ns_name)})
        ns_dict.update({NAMESPACE_VPOOL: self.get_ns_vpool(ns_name)})
        return ns_dict
