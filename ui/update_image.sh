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
source ${lib}/versioning.sh
#
##############################################################################

if ! [ -z "$1" ] && [ "$1" == "--clean" ]; then
    docker_clean
    exit 0
fi

o "Updating image: ${image_name}"
o "Build context is: ${context}"

if ${proxy_flag:-false}; then
    PipProxy="-var PipProxy=${proxy_val}"
    o "Tunneling through proxy: ${proxy_val}"
else
    PipProxy=''
fi

docker_clean

o "Collecting artifacts"
collect_artifacts

o "UI is: ${ui_artifact}"
# o "Ansible is: ${ansible_artifact}"

if data_container_missing; then
    o "Creating new data container"
    make_new_data_container
fi

sudo docker cp ui/resources/docker/entrypoint.sh "${data_container_name}:/usr/local/bin/entrypoint.sh"
sudo docker cp ${etc}/release.conf "${data_container_name}:/etc/release.conf"
sudo docker cp bootstrap.conf "${data_container_name}:/etc/auto.conf"
# sudo docker cp "${ansible_artifact}" "${data_container_name}:/usr/local/src/ansible.tgz"
sudo docker cp "${ui_artifact}" "${data_container_name}:/usr/local/src/ui.tgz"
touch update.sem
sudo docker cp update.sem "${data_container_name}:/etc/update.sem"
rm -f update.sem

o "Image updated."
