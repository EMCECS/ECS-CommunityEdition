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
    repo_path="${registry_val}/${image_release}"
else
    repo_path="${image_release}"
fi

o "Cleaning up..."
docker_clean

#o "Login into Docker for image pull (rate limits)..."
#docker_login

o "Pulling image ${repo_path}"
sudo docker pull ${repo_path} || img_pull_fail

o "Tagging ${repo_path} -> ${image_release}"
sudo docker tag "${repo_path}" "${image_release}" || img_pull_fail

exit 0
