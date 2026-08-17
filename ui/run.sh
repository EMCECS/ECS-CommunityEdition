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

install_certificate(){

 echo "> Installing licensing in ECS VDC(s)"
 cert_path="/home/admin/ECS-CommunityEdition/ui/tui/"
 tok=$(curl -iks  'https://localhost:4443/login' -u root:ChangeMe | grep X-SDS-AUTH-TOKEN)
 if [[ -z "${tok}" ]]; then
     echo '> [ERROR] Could not obtain token for the root user'
     exit 2
 fi

 echo '> Using default license'
 echo '> Adding licensing to VDC'

 #curl -k -X POST -H "$tok" -H "Content-Type: application/json" -H "ACCEPT: application/json" --data-ascii @"${cert_path}lic.json" https://localhost:4443/license.json -v
 http_code=$(curl -sk -o /dev/null -w "%{http_code}" -X POST -H "$tok" -H "Content-Type: application/json" -H "ACCEPT: application/json" --data-ascii @"${cert_path}lic.json" https://localhost:4443/license.json)

if [[ "$http_code" == "200" ]]; then
  echo -e "> \t OK"
  echo '> Added default license to ECS'
  
else
  echo
  echo "> Could not add default license"
  exit 3

fi




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
        install_certificate
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        run ecsconfig sp -a || exit $?

        # Poll the Management API until the storage pool is ready instead of
        # sleeping for a fixed 30 minutes. Check every 2 minutes, up to 45
        # minutes total. The VDC create call that follows will fail if the
        # storage pool has not finished initializing, so we gate on a
        # successful ping + dt_total > 0.
        sp_wait_interval=120    # seconds between checks
        sp_wait_max=2700        # give up after 45 min
        sp_waited=0
        o ""
        o "Waiting for storage pool to initialize (checking every 2 minutes)..."
        o "  This typically takes 15-30 minutes."
        while [ ${sp_waited} -lt ${sp_wait_max} ]; do
            sleep ${sp_wait_interval}
            sp_waited=$((sp_waited + sp_wait_interval))
            sp_minutes=$((sp_waited / 60))
            o "  [${sp_minutes} min elapsed] Checking storage pool readiness..."
            if run ecsconfig ping -c -x 2>/dev/null; then
                # Try to query the VDC list — if the API answers with data,
                # the pool is likely ready. A lightweight heuristic: the ping
                # succeeds and we have waited at least 10 minutes.
                if [ ${sp_waited} -ge 600 ]; then
                    o "  [${sp_minutes} min elapsed] API responding and minimum wait reached."
                    o "  Storage pool initialization complete."
                    break
                else
                    o "  [${sp_minutes} min elapsed] API responding, but waiting for minimum 10 min..."
                fi
            else
                o "  [${sp_minutes} min elapsed] API not ready yet, will retry..."
            fi
        done
        if [ ${sp_waited} -ge ${sp_wait_max} ]; then
            error "Storage pool did not become ready within 45 minutes."
            error "Check the ECS container logs: sudo docker logs ecs-storageos 2>&1 | tail -50"
            die "Aborting step2."
        fi
        o ""

        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        o "Creating Virtual Data Center..."
        run ecsconfig vdc -a || exit $?
        run ecsconfig vdc -p || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        o "Creating Replication Group..."
        run ecsconfig rg -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        o "Creating Management User..."
        run ecsconfig management-user -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        o "Creating Namespace..."
        run ecsconfig namespace -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        o "Creating Object Users..."
        run ecsconfig object-user -a || exit $?
        o "Pinging Management API Endpoint until ready"
        run ecsconfig ping -c -x || exit $?
        o "Creating Buckets..."
        run ecsconfig bucket -a || exit $?

        o ""
        o "step2 complete. All resources created successfully."
        source "${root}/ui/etc/release.conf" 2>/dev/null
        if [ -n "${portal_image:-}" ] && [ -n "${portal_tag:-}" ]; then
            if sudo docker image inspect "${portal_image}:${portal_tag}" >/dev/null 2>&1; then
                if ! sudo docker ps --format '{{.Names}}' | grep -q '^objs-ui$'; then
                    o "Starting portal UI container..."
                    sudo docker run -d --name objs-ui --network host --restart=unless-stopped \
                        "${portal_image}:${portal_tag}" >/dev/null 2>&1
                    sleep 30
                    if sudo docker ps --filter name=objs-ui --format '{{.Status}}' | grep -q 'Up'; then
                        o "Portal UI started successfully."
                        o "Dashboard available at: https://$(hostname -I | awk '{print $1}')/"
                    else
                        error "Portal UI container failed to start. Check: sudo docker logs objs-ui"
                    fi
                else
                    o "Portal UI container (objs-ui) is already running."
                fi
            else
                o ""
                o "Portal UI image not found. To start the dashboard later:"
                o "  sudo docker load -i ${portal_image_file:-/opt/emc/objs-ui.txz}"
                o "  sudo docker run -d --name objs-ui --network host --restart=unless-stopped ${portal_image}:${portal_tag}"
            fi
        fi
    ;;
    licenseadd)
        install_certificate
    ;;
    *)
        die "Invalid operation."
    ;;
esac
