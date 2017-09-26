#!/usr/bin/env python
from __future__ import print_function
import sys
import json

INSTALL_NODE_KEY = "install_node_ip"
ECS_NODE_KEY = "ecs_node_ip"
SSH_BINARY = "/usr/bin/ssh"
SSH_ARGS = ""
SSH_USER = sys.argv[3]

def main():
    if len(sys.argv) != 4:
        print("Usage: %s INPUT_JSON_FILE OUTPUT_HOSTS_FILE SSH_USER" % (sys.argv[0],))
        sys.exit(1)

    with open(sys.argv[1]) as json_file:
        data = json.load(json_file)

    ssh_command = "{} {} {}@{} $*".format(SSH_BINARY, SSH_ARGS, SSH_USER, data[INSTALL_NODE_KEY]["value"])

    with open(sys.argv[2], "w") as ssh_script:
        ssh_script.write("#!/usr/bin/env bash\n")
        ssh_script.write("%s\n" % ssh_command)
        ssh_script.write("\n")

if __name__ == "__main__":
    main()
