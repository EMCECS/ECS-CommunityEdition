#!/usr/bin/env bash

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

if data_container_missing; then
    make_new_data_container
fi

run() {
    run="${1}"
    shift
    sudo docker run --rm -it --privileged --net=host ${default_mount_opts[@]} ${latest_image_path} ${run} ${@}
    return $?
}

case "$(basename ${0})" in
    update_image)
        cd "${root}"
        "${root}/ui/update_image.sh"
        cd -
    ;;
    rebuild_image)
        cd "${root}"
        "${root}/ui/build_image.sh" --clean
        "${root}/ui/build_image.sh"
        cd -
    ;;
    update_deploy)
        if ${deploy_flag}; then
            o "Updating /opt/emc/ecs-install/deploy.yml from ${deploy_val}"
            cd "${root}"
            sudo cp "${deploy_val}" /opt/emc/ecs-install/deploy.yml
            ecsdeploy load
            cd -
        else
            o "No deploy.yml file was provided during bootstrap. To use this feature, do the following:"
            o "Modify ${root}/bootstrap.conf by adjusting the following lines:"
            o "     deploy_flag=true"
            o "     deploy_val=<path to your deploy.yml>"
        fi
    ;;
    ecsdeploy|ecsconfig|ecsremove|catfacts|enter|pingnodes)
        run "$(basename ${0})" ${@} || exit $?
    ;;
    island-step1)
        #run ecsdeploy load || exit $?
        run ecsdeploy cache || exit $?
    ;;
    island-step2)
        #run ecsdeploy load || exit $?
        run ecsdeploy access check || exit $?
        run ecsdeploy deploy || exit $?
        run ecsdeploy reboot || exit $?
        run ping_until_clear
        run ecsdeploy start || exit $?
    ;;
    step1)
        #run ecsdeploy load || exit $?
        run ecsdeploy access check cache || exit $?
        run ecsdeploy deploy || exit $?
        run ecsdeploy reboot || exit $?
        run ping_until_clear
        run ecsdeploy start || exit $?
    ;;
    step2|island-step3)
        run ecsconfig ping -c -x || exit $?
        run ecsconfig licensing -a || exit $?
        run ecsconfig ping -c -x || exit $?
        run ecsconfig sp -a || exit $?
        run ecsconfig ping -c -x || exit $?
        run ecsconfig vdc -a || exit $?
        run ecsconfig ping -c -x || exit $?
        run ecsconfig rg -a || exit $?
        run ecsconfig ping -c -x || exit $?
    ;;
    *)
        die "Invalid operation."
    ;;
esac
