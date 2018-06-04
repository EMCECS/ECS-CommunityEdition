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
elif ! [ -z "$1" ] && [ "$1" == "--update-mirror" ]; then
    if [ -z "$2" ]; then
        die "You must provide a valid Alpine Linux mirror URL."
    else
        alpine_mirror="${2}"
        build_image_flag=true
        export build_image_flag
        export alpine_mirror
        o "Updating bootstrap.conf to use Alpine Linux mirror ${alpine_mirror}"
        dump_bootstrap_config > "${root}/bootstrap.conf"
        exit 0
    fi
fi

build_push=false

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
        # BuildPush="--push ${BuildPush}"
        build_push=true
        o "I will push a release image to the registry after build"
    ;;

esac

o "Cleaning up..."
docker_clean

o "Checking Alpine Linux mirror"
alpine_mirror_test="${alpine_mirror}/MIRRORS.txt"
if ! is_file_http_accessible "${alpine_mirror_test}" 2>&1 >/dev/null; then
    error "We couldn't validate the provided Alpine Linux mirror my checking that"
    error "the following file is accessible:"
    error ""
    error "${alpine_mirror_test}"
    error ""
    error "Please check the mirror URL and try again.  You may need to update the"
    error "configured Alpine Linux mirror by running the following command:"
    error "'${0} --update-mirror <mirror URL>'"
    die "If you still have troubles, please reach out to us us on GitHub."
fi

o "Generating Alpine Linux repositories file"
create_apk_repositories

o "Collecting artifacts"
collect_artifacts

Context="-var Context=${context}"
Artifacts=""
# Currently using the Ansible apk
# Artifacts="${Artifacts} -var AnsibleArtifact=${ansible_artifact}"
Artifacts="${Artifacts} -var UIArtifact=${ui_artifact}"
Version="-var Version=${dockerhub_image_path}"
Rockerfile="-f ui/resources/docker/Rockerfile"

o "UI artifact is: ${ui_artifact}"
# Currently using the Ansible apk
# o "Ansible artifact is: ${ansible_artifact}"
sudo /usr/local/bin/rocker build $Context $Version $Artifacts $FromImage $Rockerfile $HTTPProxy $PipProxy . || img_build_fail

o "Tagging ${dockerhub_image_path} -> ${full_image_path}"
sudo docker tag "${dockerhub_image_path}" "${full_image_path}" || img_pull_fail
o "Tagging ${dockerhub_image_path} -> ${image_release}"
sudo docker tag "${dockerhub_image_path}" "${image_release}" || img_pull_fail

if ${build_push}; then
    o "Pushing to local repo"
    sudo docker push "${full_image_path}"
    if docker_login; then
        o "Pushing to DockerHub"
        sudo docker push "${dockerhub_image_path}"
    fi
fi

exit 0
