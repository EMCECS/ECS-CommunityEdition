#!/usr/bin/env bash

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# A basic ISO-8601 timestamp with strict capability
timestamp() {
    local _char=' '
    if [ "${*}" == "strict" ]; then
        _char='T'
    fi
    printf "%(%Y-%m-%d${_char}%H:%M:%S%z)T\n" -1
}

# Get epoch seconds of now
epoch_now() {
    printf "%(%s)T\n" -1
}

# Die if a file doesn't exist (with description)
ensure_file_exists() {
    local filepath="${1}"
    shift
    local filedesc="${*}"

    if ! [ -f "${filepath}" ]; then
        die "Can't find ${filedesc} file at ${filepath}"
    fi
}

ensure_string_matches() {
    local needle="${1}"
    shift
    local haystack="${1}"
    shift
    local message="${*}"
    if ! echo "${haystack}" | grep "${needle}" >/dev/null; then
        die "${message}"
    fi
}

ensure_string_list_matches() {
    local needles="${1}"
    shift
    local haystack="${1}"
    shift
    local message="${*}"
    local found=false
    for needle in ${needles/,/ }; do
        if echo "${haystack}" | grep "${needle}" >/dev/null; then
           found=true
        fi
    done
    ! $found && die "${message}"
}

# The missing privileged file "redirection" command
append() {
    sudo dd status=none oflag=append conv=notrunc of="${1}"
}

collect_environment_info() {
#    if $container_flag; then
#        o "Running in a container, skipping collection"
#    else

        qlog "GET-HWINFO"
        sudo dmesg 2>&1 | qlog
        qlog "END-DMESG"
        sudo uname -a 2>&1 | qlog
        qlog "END-UNAME"
        env 2>&1 | qlog
        qlog "END-ENV"
        sudo lsmod 2>&1 | qlog
        qlog "END-LSMOD"
        sudo lscpu 2>&1 | qlog
        qlog "END-LSCPU"
        sudo lspci 2>&1 | qlog
        qlog "END-LSPCI"
        sudo lsscsi 2>&1 | qlog
        qlog "END-LSSCSI"
        sudo lsusb 2>&1 | qlog
        qlog "END-LSUSB"
        sudo lshw 2>&1 | qlog
        qlog "END-LSHW"
        sudo hwinfo 2>&1 | qlog
        qlog "END-HWINFO"
        sudo dmidecode 2>&1 | qlog
        qlog "END-DMIDECODE"
        sudo free -h 2>&1 | qlog
        qlog "END-FREE"
        sudo df -h 2>&1 | qlog
        qlog "END-DF"
        sudo mount 2>&1 | qlog
        qlog "END-MOUNT"
        sudo fdisk -l 2>&1 | qlog
        qlog "END-FDISK"
        sudo parted -l 2>&1 | qlog
        qlog "END-PARTED"
        sudo pvs 2>&1 | qlog
        qlog "END-PVS"
        sudo vgs 2>&1 | qlog
        qlog "END-GVS"
        sudo lvs 2>&1 | qlog
        qlog "END-LVS"
        log "END-COLLECT-ENVIRONMENT-INFO"
#    fi
}

proxy_http_ping() {
    echo "curl -sSLfI -w '%{http_code}' -x ${1} --proxytunnel ${2} -o /dev/null -m 10" | log
    curl -sSLfI -w '%{http_code}' -x ${1} --proxytunnel ${2} -o /dev/null -m 10
    return ${?}
}

is_file_http_accessible() {
    if $proxy_flag; then
        echo "curl -sSLfI -w '%{http_code}' -x ${proxy_val} --proxytunnel ${1} -o /dev/null -m 10" | log
        curl -sSLfI -w '%{http_code}' -x ${proxy_val} --proxytunnel ${1} -o /dev/null -m 10
        return ${?}
    else
        echo "curl -sSLfI -w '%{http_code}' ${1} -o /dev/null -m 10" | log
        curl -sSLfI -w '%{http_code}' ${1} -o /dev/null -m 10
        return ${?}
    fi
}

ping_sudo() {
    retry_with_timeout 5 1800 sudo -v
}

quit_sudo() {
    sudo -k
}

dump_bootstrap_config() {
    _vars="override_flag"
    _vars="$_vars override_val"
    _vars="$_vars mitm_flag"
    _vars="$_vars mitm_val"
    _vars="$_vars proxy_flag"
    _vars="$_vars proxy_val"
    _vars="$_vars proxy_test_flag"
    _vars="$_vars proxy_test_val"
    _vars="$_vars build_image_flag"
    _vars="$_vars alpine_mirror"
    _vars="$_vars registry_flag"
    _vars="$_vars registry_val"
    _vars="$_vars regcert_flag"
    _vars="$_vars regcert_val"
    _vars="$_vars vm_flag"
    _vars="$_vars docker_flag"
    _vars="$_vars verbose_flag"
    _vars="$_vars quiet_flag"
    _vars="$_vars minimal_flag"
    _vars="$_vars deploy_flag"
    _vars="$_vars deploy_val"
    _vars="$_vars mirror_flag"
    _vars="$_vars mirror_val"
    _vars="$_vars DEVEL"
    _vars="$_vars DRONE"
    _vars="$_vars BUILD"
    _vars="$_vars INSTALL_ROOT"

    for _var in $_vars; do
        eval echo "export $_var=\$$_var"
    done
}

# Simple retry loop with timeout
# retry_with_timeout <attempts> <timeout_seconds> <command>
retry_with_timeout() {
    local _attempts="${1}"
    local _timeout="${2}"
    shift; shift
    local _cmd="${*}"

    local _attempt=0
    local _timeout_time="$(( $(epoch_now) + _timeout))"

    while [[ _attempt < _attempts ]] && [[ "$(epoch_now)" < "${_timeout_time}" ]] && ! $_cmd; do
        ((_attempt++))
        sleep 1
    done
}

retry_until_ok() {
    local _cmd="${*}"
    while ! $_cmd; do
        o "Command failed, retrying..."
    done
}
