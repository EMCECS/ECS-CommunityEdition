#!/bin/ash
set -o pipefail

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

facts="/var/cache/emc/ecs-install/facts"
host="${1}"

usage() {
    echo "Usage: \$ catfacts <Ansible inventory host>"
    echo "Here is a list of hosts you can query:"
    echo "Data Node(s):"
    ansible --list-hosts data_node
    echo "Install Node:"
    ansible --list-hosts install_node
}

if ! [ -z "${host}" ]; then
    if [ -f "${facts}/${host}" ]; then
        jq -CS . "${facts}/${host}" | less -R
    else
        echo "host '${host}' does not (yet) have facts registered in the fact cache"
        exit 1
    fi
else
    usage
    exit 1
fi

exit 0
