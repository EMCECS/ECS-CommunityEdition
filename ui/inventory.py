#!/usr/bin/env python
# coding=utf-8

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import tui
import simplejson
from tui.ecsconf import *
from pprint import pprint

"""
# Logging
"""


logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


"""
# Helpers
"""


"""
# Config
"""

debug = False

"""
# Commands
"""


def d(obj):
    """
    pprint something when debug = True
    :param obj:
    :return: n/a
    """
    if debug is True:
        pprint(obj)


def inventory():
    """
    Ansible dynamic inventory script
    """
    conf = tui.Director()
    conf.load_deploy()
    conf.ecs = tui.ECSConf(conf.deploy)

    hostvars = {}
    pool_groups = {}

    # Get all the storage pools
    pools = conf.ecs.get_sp_names()

    # Get install node
    install_node = conf.deploy.facts.install_node

    # Generate the data node group metadata
    for sp in pools:
        pool_groups[sp] = {}
        pool_groups[sp]['hosts'] = []
        for node in conf.ecs.get_sp_members(sp):
            pool_groups[sp]["hosts"].append(node)
        pool_groups[sp]["vars"] = {}
        pool_groups[sp]["vars"].update(conf.ecs.get_node_defaults())
        pool_groups[sp]["vars"].update(conf.ecs.get_sp_options(sp))

    # Dump all the VDCs
    # vdcs = conf.ecs.get_vdc_names()
    # vdc_groups = {}
    # Dump all the VDC memberships
    # for vdc in vdcs:
    #     vdc_groups.update({vdc: {"hosts": []}})
    #     for sp in conf.ecs.get_vdc_members(vdc):
    #         for node in conf.ecs.get_sp_members(sp):
    #             vdc_groups[vdc]["hosts"].append(node)
    #             hostvars.update({"vdc": vdc})

    # Dump localhost
    hostvars["localhost"] = {}

    # Dump global node hostvars (this is where the ansible creds get put)
    fun_facts = conf.ecs.get_fun_facts()

    for node in conf.ecs.list_all_nodes():
        hostvars[node] = fun_facts.copy()

    # Dump SP node hostvars
    for node in conf.ecs.list_all_sp_nodes():
        d(node)
        d(hostvars[node])
        d('add vdc')
        hostvars[node]["vdc"] = conf.ecs.get_node_vdc(node)
        d(hostvars[node])

    d('--- new hostvars ---')
    d(hostvars)

    # Build the inventory tree
    inventory_list = {"data_node": {"children": pools,
                                    "vars": {}
                                    },
                      "install_node": {"hosts": [install_node],
                                       "vars": conf.ecs.get_node_options(install_node)
                                       },
                      "ecs_install": {"hosts": ["localhost"],
                                      "vars": {
                                          "ansible_become": False,
                                          "ansible_connection": "local",
                                          "ansible_python_interpreter": "/usr/local/bin/python"
                                      }
                                      },
                      "_meta": {
                          "hostvars": hostvars
                                }
                      }

    # Add the storage pool groups
    inventory_list.update(pool_groups)
    inventory_list["data_node"]["vars"].update(conf.ecs.get_node_defaults())
    inventory_list["data_node"]["vars"].update(conf.ecs.get_defaults(SP))

    print simplejson.dumps(inventory_list)

if __name__ == '__main__':
    inventory()
