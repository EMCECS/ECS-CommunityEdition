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

o "Building image ${image_name}"
o "Build context is: ${context}"

FromImage=${from_image}
if $registry_flag; then
    o "Using custom registry: ${registry_val}"
    FromImage="-var FromImage=${registry_val}/${FromImage}"
else
    FromImage="-var FromImage=${FromImage}"
fi

if ${proxy_flag:-false}; then
    PipProxy="-var PipProxy=${proxy_val}"
    HTTPProxy="-var HTTPProxy=http://${proxy_val}"
    o "Tunneling through proxy: ${proxy_val}"
else
    PipProxy=''
    HTTPProxy=''
fi

BuildPush="-var BuildPush=${latest_image_path}"

case $context in

    release)
        BuildPush="--push ${BuildPush}"
        o "I will push a release image to the registry after build"
    ;;

esac

o "Collecting artifacts"
collect_artifacts

Context="-var Context=${context}"
Artifacts="-var AnsibleArtifact=${ansible_artifact}"
Artifacts="${Artifacts} -var UIArtifact=${ui_artifact}"
Version="-var Version=${full_image_path}" # Yes, really
Rockerfile="-f ui/resources/docker/Rockerfile"

o "UI artifact is: ${ui_artifact}"
o "Ansible artifact is: ${ansible_artifact}"

sudo /usr/local/bin/rocker build $Context $Version $Artifacts $FromImage $BuildPush $Rockerfile $HTTPProxy $PipProxy . || img_build_fail

exit 0
