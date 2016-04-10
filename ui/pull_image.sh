#!/usr/bin/env bash
shopt -s extglob
shopt -s xpg_echo
set -o pipefail

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

##### Boilerplate ############################################################
# The build environment is always determined by the last bootstrap.sh run
source "$HOME/.ecsinstallrc"
source ${INSTALL_ROOT}/bootstrap.conf
root=${INSTALL_ROOT}
lib=${root}/ui/libexec
cd ${root}
#
# Imports and import configs
source ${lib}/includes.sh
#
##############################################################################

if ! [ -z "$1" ] && [ "$1" == "--clean" ]; then
    docker_clean
    exit 0
fi

registry_flag=${registry_flag:-false}

if $registry_flag; then
    repo_path="${registry_val}/${repo_name}"
else
    repo_path="${repo_name}"
fi

o "Pulling image ${image_release}"
sudo docker pull ${image_release} 2>&1 | log || die img_pull_fail

exit 0
