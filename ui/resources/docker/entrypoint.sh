#!/bin/ash

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# I am a stupid simple init replacement

prefix="/usr/local/src"
root="${prefix}/ui"
ansible="${root}/ansible"
name="ecs-install"
init_container=false
log_path="/var/log/ecs-install.container.log"
rc=0

o() {
    echo -e "${name}> $*" | tee -a ${log_path}
}

n() {
    echo -en "${name}> $*"
    echo -e "${name}> $*" >> ${log_path}
}

cond_incr_rc() {
    if [ ${rc} -lt ${1} ]; then
        rc=${1}
    fi
}

unpack() {
    package="${1}"
    installcmd="${2}"
    if [ -f "${prefix}/${package}" ]; then

        # Work in src dir
        cd "${prefix}"

        # Remove previous copy
        if [ -d "${prefix}/$(basename ${package} .tgz)" ]; then
            rm -rf "${prefix}/$(basename ${package} .tgz)"
        fi
        cd "${prefix}"
        if ! tar -xzf "${package}"; then
            o "${package} failed to unpack"
            return 1
        fi
        if ! cd "${prefix}/$(basename ${package} .tgz)"*; then
            o "${package} failed, could not cd to $(basename ${package} .tgz)"
            return 1
        fi

        if ! ${installcmd}; then
            o "${package} failed to build."
            return 1
        fi

    else
        o "Couldn't install ${package}, is the image built correctly?"
        return 1
    fi
}

torrent() {
    if [ -f /opt/ffx.sem ]; then
        n "Init bittorrent ffx "
        opentracker -i 0.0.0.0 -p 6881 -P 6881 -d /var/run/opentracker -u nobody &
        echo -n "."
        cd /var/cache/emc
        aria2c -q -l /var/log/torrent.log -T /var/cache/emc/ecs-install/cache.torrent --seed-ratio=0.0 \
               --dht-listen-port=6882 --allow-overwrite=true --check-integrity \
               --listen-port=6883-6999 --enable-mmap=true 1>/dev/null 2>/dev/null &
        echo -n ". "
        cd /
        echo "OK"
    fi
}

condkill() {
    process="${1}"
    signal="${2}"
    if ! [ -z "$(pgrep ${process})" ];
        then kill "${signal}" "$(pgrep ${process})"
        return 1
    else
        return 0
    fi
}

retry() {
    local tries=0
    until $@ || [ ${tries} -ge 3 ]; do
        sleep 1
        tries=$((tries++))
    done
}

# Nicely kill off background processes
simple_shutdown() {
    processlist="${@}"

    for process in $processlist; do
        retry condkill "${process}" "-INT" &
    done
    wait
    cond_incr_rc $?
    for process in $processlist; do
        retry condkill "${process}" "-TERM" &
    done
    wait
    cond_incr_rc $?
    for process in $processlist; do
        retry condkill "${process}" "-KILL" &
    done
    wait
    cond_incr_rc $?
}

we_get_signal() {
    # o "Caught signal; preventing zombie attack..."
    simple_shutdown aria2c opentracker
    # o "Phweew, that was close!"
    exit $rc
}

# Because Docker zombies are real.
trap we_get_signal INT TERM

# if ! [ -x /usr/bin/ansible ] || ! [ -x /usr/bin/ecsdeploy ]; then
if ! [ -x /usr/bin/ecsdeploy ]; then
    #o "No /usr/bin/ecsdeploy found"
    init_container=true
fi

if [ -f /etc/update.sem ]; then
    #o "Found /etc/update.sem"
    rm -f /etc/update.sem
    init_container=true
fi

if $init_container; then
    n "Initializing data container, one moment "
    /usr/sbin/update-ca-certificates 1>/dev/null 2>/dev/null
    echo -n "."
    mkdir -p /var/cache/apk
    # echo -n "."
    # unpack ansible.tgz "pip install -q ."
    echo -n "."
    unpack ui.tgz "pip install -q ."
    cond_incr_rc $?
    # echo -n "."
    # Version hack Ansible when installing to site-packages
    # echo "__version__ = '2.1.0.dev.ecs-install'" > /usr/local/lib/python2.7/site-packages/ansible/__init__.py
    echo -n ". "
    echo "OK"
fi

if ! [ -f "/usr/local/src/ui/ansible/group_vars/all" ]; then
    o "Applying and validating deploy.yml..."
    ecsdeploy load
fi

if ! [ -z "$*" ]; then
# ecsdeploy catfacts enter nodeping
    case "${1}" in
        enter)
            torrent
            if [ -z "${2}" ]; then
                /bin/ash -l
            else
                ansible_user="$(grep '^ *ssh_username:' /opt/deploy.yml | awk '{print $2}')"
                /usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i /opt/ssh/id_rsa -i /opt/ssh/id_ed25519 "${ansible_user}"@"${2}"
            fi
            cond_incr_rc $?
            ;;
        catfacts)
            shift
            cd "${ansible}"
            ash "${ansible}/catfacts.sh" ${@}
            cond_incr_rc $?
            ;;
        inventory)
            shift
            inventory | jq
            cond_incr_rc $?
            ;;
        pingnodes)
            shift
            cd "${ansible}"
            if [ -z "${@}" ]; then
                hostspec="data_node"
            else
                hostspec="${@}"
            fi
            ansible -m ping ${hostspec}
            cond_incr_rc $?
            ;;
        ping_until_clear)
            shift
            cd "${root}"
            echo "Waiting for nodes to become reachable... (CTRL-C to break)"
            until ansible data_node -o -m ping; do
                sleep 10
            done
            ;;
        ecsdeploy)
            torrent
            cd "${root}"
            ${@}
            cond_incr_rc $?
            ;;
        testbook)
            torrent
            cd /ansible
            ansible-playbook testing.yml
            cond_incr_rc $?
            ;;
        *)
            ${@}
            cond_incr_rc $?
            ;;
    esac

else
    ecsdeploy --help
fi

simple_shutdown aria2c opentracker
#o "Exit code: ${rc}"
exit $rc
