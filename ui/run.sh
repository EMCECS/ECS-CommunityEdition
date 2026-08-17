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
        # Clean stale lock files that can cause storageos boot failures
        sudo rm -f /tmp/systool.lock
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
        # Clean stale lock files that can cause storageos boot failures
        sudo rm -f /tmp/systool.lock
        #run ecsdeploy load || exit $?
        run ecsdeploy access || exit $?
        run ecsdeploy check || exit $?
        run ecsdeploy bootstrap || exit $?
        run ecsdeploy deploy || exit $?
        run ecsdeploy start || exit $?
    ;;
    step1)
        # Clean stale lock files that can cause storageos boot failures
        sudo rm -f /tmp/systool.lock
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

        # -----------------------------------------------------------------
        # Helper: retry a command with delay between attempts.
        #   retry_cmd <max_attempts> <delay_secs> <description> <cmd...>
        # Prints a status line every attempt. Never exits the script on
        # failure — returns 0 on success, 1 if all attempts exhausted.
        # -----------------------------------------------------------------
        retry_cmd() {
            local _max=${1}; shift
            local _delay=${1}; shift
            local _desc="${1}"; shift
            local _attempt=1
            while [ ${_attempt} -le ${_max} ]; do
                o "  [attempt ${_attempt}/${_max}] ${_desc}..."
                if "${@}"; then
                    o "  ${_desc} — succeeded."
                    return 0
                fi
                if [ ${_attempt} -lt ${_max} ]; then
                    o "  ${_desc} — failed, retrying in ${_delay}s..."
                    sleep ${_delay}
                fi
                _attempt=$((_attempt + 1))
            done
            error "${_desc} — failed after ${_max} attempts."
            return 1
        }

        # -----------------------------------------------------------------
        # Phase 1: Wait for Management API to become responsive
        # -----------------------------------------------------------------
        o ""
        o "=========================================="
        o " step2: Configuring OBS CE"
        o "=========================================="
        o ""
        o "[Phase 1/8] Waiting for Management API..."
        retry_cmd 30 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?

        # -----------------------------------------------------------------
        # Phase 2: Install license
        # -----------------------------------------------------------------
        o ""
        o "[Phase 2/8] Installing license..."
        retry_cmd 5 60 "Installing license" \
            install_certificate || exit $?

        o ""
        o "Pinging Management API after license install..."
        retry_cmd 10 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?

        # -----------------------------------------------------------------
        # Phase 3: Create Storage Pool + add data stores
        #   This is the step most likely to fail if services are still
        #   initializing. Retry with generous delays.
        # -----------------------------------------------------------------
        o ""
        o "[Phase 3/8] Creating Storage Pool..."
        o "  (Services may still be initializing — will retry up to 20"
        o "   times with 2 min delay between attempts, ~40 min max)"
        retry_cmd 20 120 "Creating Storage Pool" \
            run ecsconfig sp -a || exit $?

        # -----------------------------------------------------------------
        # Wait for storage pool to fully initialize before proceeding.
        # The VDC create call will fail if the pool is not ready.
        # Check every 1 minute, up to 45 minutes.
        # -----------------------------------------------------------------
        o ""
        o "[Phase 3/8] Waiting for storage pool to initialize..."
        o "  This typically takes 15-30 minutes. Checking every 1 minute."
        sp_wait_interval=60     # seconds between checks
        sp_wait_max=2700        # give up after 45 min
        sp_waited=0
        while [ ${sp_waited} -lt ${sp_wait_max} ]; do
            sleep ${sp_wait_interval}
            sp_waited=$((sp_waited + sp_wait_interval))
            sp_minutes=$((sp_waited / 60))
            if run ecsconfig ping -c -x 2>/dev/null; then
                if [ ${sp_waited} -ge 600 ]; then
                    o "  [${sp_minutes} min] API responding and minimum wait (10 min) reached."
                    o "  Storage pool initialization complete."
                    break
                else
                    o "  [${sp_minutes} min] API responding, waiting for minimum 10 min..."
                fi
            else
                o "  [${sp_minutes} min] API not ready yet, will retry..."
            fi
        done
        if [ ${sp_waited} -ge ${sp_wait_max} ]; then
            error "Storage pool did not become ready within 45 minutes."
            error "Check: sudo docker logs ecs-storageos 2>&1 | tail -50"
            die "Aborting step2."
        fi

        # -----------------------------------------------------------------
        # Phase 4: Create Virtual Data Center
        # -----------------------------------------------------------------
        o ""
        o "[Phase 4/8] Creating Virtual Data Center..."
        retry_cmd 10 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?
        retry_cmd 10 60 "Creating VDC" \
            run ecsconfig vdc -a || exit $?
        retry_cmd 5 60 "Populating VDC" \
            run ecsconfig vdc -p || exit $?

        # -----------------------------------------------------------------
        # Phase 5: Create Replication Group
        # -----------------------------------------------------------------
        o ""
        o "[Phase 5/8] Creating Replication Group..."
        retry_cmd 10 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?
        retry_cmd 10 60 "Creating Replication Group" \
            run ecsconfig rg -a || exit $?

        # -----------------------------------------------------------------
        # Phase 6: Create Management User
        # -----------------------------------------------------------------
        o ""
        o "[Phase 6/8] Creating Management User..."
        retry_cmd 10 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?
        retry_cmd 10 60 "Creating Management User" \
            run ecsconfig management-user -a || exit $?

        # -----------------------------------------------------------------
        # Phase 7: Create Namespace, Object Users, Buckets
        # -----------------------------------------------------------------
        o ""
        o "[Phase 7/8] Creating Namespace, Object Users, and Buckets..."
        retry_cmd 10 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?
        retry_cmd 10 60 "Creating Namespace" \
            run ecsconfig namespace -a || exit $?

        retry_cmd 10 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?
        retry_cmd 10 60 "Creating Object Users" \
            run ecsconfig object-user -a || exit $?

        retry_cmd 10 60 "Pinging Management API" \
            run ecsconfig ping -c -x || exit $?
        retry_cmd 10 60 "Creating Buckets" \
            run ecsconfig bucket -a || exit $?

        # -----------------------------------------------------------------
        # Phase 8: Start Portal UI container
        # -----------------------------------------------------------------
        o ""
        o "[Phase 8/8] Starting Portal UI..."
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
                o "  sudo docker pull ${portal_image}:${portal_tag}"
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
