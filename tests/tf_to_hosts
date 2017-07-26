#!/usr/bin/env python
from __future__ import print_function
import sys
import json

INSTALL_NODE_KEY = "install_node_ip"
ECS_NODE_KEY = "ecs_node_ip"

def main():
    if len(sys.argv) != 3:
        print("Usage: %s INPUT_JSON_FILE OUTPUT_HOSTS_FILE" % (sys.argv[0],))
        sys.exit(1)

    with open(sys.argv[1]) as json_file:
        data = json.load(json_file)

    with open(sys.argv[2], "w") as hosts_file:
        hosts_file.write("[install_node]\n")
        hosts_file.write("%s ansible_connection=ssh\n" % (data[INSTALL_NODE_KEY]["value"]))
        hosts_file.write("\n[ecs_nodes]\n")
        for ip in data[ECS_NODE_KEY]["value"]:
            hosts_file.write("%s ansible_connection=ssh\n" % (ip,))

if __name__ == "__main__":
    main()
