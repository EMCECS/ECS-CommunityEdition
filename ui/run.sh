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

    local _interactive=''
    if ${IS_TTY}; then
        _interactive='-t'
    fi

    sudo docker run --rm -i ${_interactive} --privileged --net=host \
            ${default_mount_opts[@]} ${image_release} \
            ${run} ${@}
    rc=$?

    echo ''
    return ${rc}
}

case "$(basename ${0})" in
    videploy)
        if ${deploy_flag}; then
            vim ${deploy_val}
            update_deploy
        else
            update_deploy
        fi
    ;;
    update_image)
        cd "${root}"
        "${root}/ui/update_image.sh" ${*}
        cd - 2>&1 >/dev/null
    ;;
    build_image)
        cd "${root}"
        "${root}/ui/build_image.sh" ${*}
        cd - 2>&1 >/dev/null
    ;;
    rebuild_image)
        cd "${root}"
        "${root}/ui/build_image.sh" --clean
        "${root}/ui/build_image.sh"
        cd - 2>&1 >/dev/null
    ;;
    update_deploy)
        if ! [ -z "${1}" ]; then
            deploy_file="$(realpath ${1})" || die "deploy.yml path must be relative to ${root} or absolute"
            deploy_flag=true
            deploy_val="${deploy_file}"
            export deploy_flag
            export deploy_val
            o "Updating bootstrap.conf to use deploy config from ${deploy_val}"
            dump_bootstrap_config > "${root}/bootstrap.conf"
        fi

        if ${deploy_flag}; then
            o "Updating /opt/emc/ecs-install/deploy.yml from ${deploy_val}"
            if [ -f /opt/emc/ecs-install/deploy.yml ]; then
                diff ${deploy_val} /opt/emc/ecs-install/deploy.yml
            fi
            cd "${root}"
            sudo cp "${deploy_val}" /opt/emc/ecs-install/deploy.yml
            o "Recreating ecs-install data container"
            # update_image
            remove_data_container
            make_new_data_container
            ecsdeploy noop
            # docker_set_artifact
            cd - 2>&1 >/dev/null
        else
            o "No deploy.yml file was provided during bootstrap. To use this feature, do the following:"
            o "     $ update_deploy <FILE> "
            o "Where <FILE> is the absolute path to you deploy.yml file."
        fi
    ;;
    ecsdeploy|ecsconfig|ecsremove|catfacts|enter|pingnodes|inventory|testbook)
        run "$(basename ${0})" ${@} || exit $?
    ;;
    island-step1)
        #run ecsdeploy load || exit $?
        run ecsdeploy cache || exit $?
    ;;
    island-step2)
        #run ecsdeploy load || exit $?
        run ecsdeploy access || exit $?
        run ecsdeploy check || exit $?
        run ecsdeploy bootstrap || exit $?
        run ecsdeploy reboot || exit $?
        sleep 10
        run ping_until_clear
        run ecsdeploy deploy || exit $?
        run ecsdeploy start || exit $?
    ;;
    ova-step1)
        #run ecsdeploy load || exit $?
        run ecsdeploy access || exit $?
        run ecsdeploy check || exit $?
        run ecsdeploy bootstrap || exit $?
        run ecsdeploy deploy || exit $?
        run ecsdeploy start || exit $?
    ;;
    step1)
        #run ecsdeploy load || exit $?
        run ecsdeploy access || exit $?
        run ecsdeploy check || exit $?
        run ecsdeploy cache || exit $?
        run ecsdeploy bootstrap || exit $?
        run ecsdeploy reboot || exit $?
        run ping_until_clear
        run ecsdeploy deploy || exit $?
        run ecsdeploy start || exit $?
    ;;
    step2|island-step3|ova-step2)
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig licensing -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig sp -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig vdc -a || exit $?
        run ecsconfig vdc -p || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig rg -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig management-user -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig namespace -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig object-user -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig bucket -a || exit $?
    ;;
    *)
        die "Invalid operation."
    ;;
esac
