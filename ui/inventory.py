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


"""
# Commands
"""


def inventory():
    """
    Ansible dynamic inventory script
    """
    conf = tui.Director()
    conf.load_deploy()
    conf.ecs = tui.ECSConf(conf.deploy)

    hostvars = {}

    # Dump all the storage pools
    pools = conf.ecs.get_sp_names()
    pool_groups = {}

    # Dump all the data nodes
    for sp in pools:
        pool_groups.update({sp: {"hosts": []}})
        for node in conf.ecs.get_sp_members(sp):
            pool_groups[sp]["hosts"].append(node)
        pool_groups[sp].update({"vars": {}})
        pool_groups[sp]["vars"].update(conf.ecs.get_node_defaults())
        pool_groups[sp]["vars"].update(conf.ecs.get_sp_options(sp))

    # Dump localhost
    hostvars.update({"localhost": {}})

    # Dump hostvars (this is where the ansible creds get put)
    fun_facts = conf.ecs.get_fun_facts()
    #ansible_defaults = conf.ecs.get_attr(ANSIBLE_DEFAULTS)
    for node in conf.ecs.list_all_nodes():
        hostvars.update({node: fun_facts})

    # Dump install node
    node = conf.deploy.facts.install_node

    inventory_list = {"data_node": {"children": pools,
                                    "vars": {}
                                    },
                      "install_node": {"hosts": [node],
                                       "vars": conf.ecs.get_node_options(node)
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

    inventory_list.update(pool_groups)
    inventory_list["data_node"]["vars"].update(conf.ecs.get_node_defaults())
    inventory_list["data_node"]["vars"].update(conf.ecs.get_defaults(SP))

    print simplejson.dumps(inventory_list)

# def main():
#     parser = argparse.ArgumentParser(description='ecs-install dynamic inventory script')
#     parser.add_argument('--list', dest='get_list', action='store_true', default=False)
#     # parser.add_argument('--host', dest='host', action='store', default=None)
#     args = parser.parse_args()
#     print inventory(args)


if __name__ == '__main__':
    inventory()
