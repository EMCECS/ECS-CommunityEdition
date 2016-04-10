#@IgnoreInspection BashAddShebang

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# OS Support library for Dockerized CentOS 7.2

### Use this at your own risk, it is not at all supported
### and is only here for experimental reasons.

# Sudo pass-through
ping_sudo() {
    :
}

quit_sudo() {
    :
}

sudo() {
    ${*}
}

# Docker control socket
docker_socket='/var/run/docker.socket'

# Docker binary
docker_binary='/bin/docker'

# script to run for installing prefix_packages
in_prefix_packages() {
    :
}

# script to run for installing general_packages
in_general_packages() {
    :
}

# script to run for installing suffix_packages
in_suffix_packages() {
    # Install Rocker
    curl -fsSL https://github.com/grammarly/rocker/releases/download/1.1.2/rocker-1.1.2-linux_amd64.tar.gz \
    | sudo tar -xzC /usr/local/bin && sudo chmod +x /usr/local/bin/rocker
}

# command to run for installing vm_packages
in_vm_packages() {
    :
}

# command to install one or more os package manager package
in_repo_pkg() {
    :
}

# command to update all packages in the os package manager
up_repo_pkg_all() {
    :
}

# command to rebuild the os package manager's database
up_repo_db() {
    :
}

# command to set os package manager proxy
set_repo_proxy_conf() {
    sudo sed -i -e '/^proxy=/d' /etc/environment
    echo "proxy=${http_proxy}" \
        | append /etc/yum.conf
}

# idempotent config script to fixup repos to properly use proxycaches
set_repo_proxy_idempotent() {
    sudo sed -i -e 's/^#baseurl=/baseurl=/' /etc/yum.repos.d/*
    sudo sed -i -e 's/^mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/*
}

# command to set the proxy for the whole OS
set_os_proxy() {
    sudo sed -i -e '/_proxy/d' /etc/environment
    echo -n "http_proxy=${http_proxy}\nhttps_proxy=${http_proxy}\nftp_proxy=${http_proxy}" \
        | append /etc/environment
}

# command to determine if the OS needs restarting after package updates
get_os_needs_restarting() {
    :
}

# command to reboot the system
do_reboot() {
    :
}

# Command to configure docker's proxy under centos flavored systemd
# just goes through the motions under docker
set_docker_proxy() {
    local tmpconf="/etc/systemd/system/docker.service.d/http-proxy.conf"
    if ! [ -d "$(dirname $tmpconf)" ]; then
        sudo mkdir "$(dirname $tmpconf)"
    fi
    log "sed error is OK here if the proxy config file does not yet exist."
    sudo sed -i -e '/HTTP_PROXY/d' "$tmpconf"
    echo "Environment=\"HTTP_PROXY=${http_proxy}\" \"NO_PROXY=localhost,127.0.0.1,$(hostname),$(hostname -f)\"" \
        | append "$tmpconf"
}

# command to add mitm cert to docker trust store
# just goes through the motions under docker
set_docker_reg_cert() {
    local registry="${1}"
    local cert="${2}"
    if ! [ -d "/etc/docker/certs.d/${registry}" ]; then
        sudo mkdir -p "/etc/docker/certs.d/${registry}"
        sudo cp "${cert}" "/etc/docker/certs.d/${registry}/ca.crt"
    else
        if [ -f "/etc/docker/certs.d/${registry}/ca.crt" ]; then
            echo "Reusing existing /etc/docker/certs.d/${registry}/ca.crt"
        else
            sudo cp "${cert}" "/etc/docker/certs.d/${registry}/ca.crt"
        fi
    fi
    set_mitm_cert "${cert}"
}

# command to add mitm cert to local trust store
set_mitm_cert() {
    sudo cp "${1}" "/etc/pki/ca-trust/source/anchors/$(basename ${1}).crt"
    sudo update-ca-trust extract
}

do_post_install() {
    # Disable postfix since we don't need an MTA
    sudo systemctl disable --now postfix
    sudo mkdir -p "${docker_host_root}/ssl" "${docker_host_root}/ssh" "${docker_host_logs}"
}
