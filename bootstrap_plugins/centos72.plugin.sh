#@IgnoreInspection BashAddShebang

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# OS Support library for CentOS 7.2

os_supported=true

# Docker binary
docker_binary='/bin/docker'

# packages to clean up during preflight
# Don't `yum autoremove curl`.  Yum is a dependency and it will throw errors.
list_preflight_packages="git nfs-client nfs-tools rsync wget ntp docker vim pigz gdisk aria2 htop iotop iftop multitail dstat jq python-docker-py dkms qemu-guest-agent open-vm-tools docker"
#nfs-tools"

# Do any OS-specific tasks that must be done prior to bootstrap
do_preflight() {
    rm_repo_pkg "$list_preflight_packages"
}

# packages to install before others
list_prefix_packages='wget curl epel-release yum-utils'

# script to run for installing prefix_packages
in_prefix_packages() {
    in_repo_pkg "$list_prefix_packages"
}

# packages to install
# list_general_packages='yum-utils git python-pip python-docker-py'
list_general_packages='git ntp docker vim rsync pigz gdisk aria2'

# script to run for installing general_packages
in_general_packages() {
    in_repo_pkg "$list_general_packages"
#    if ! docker version; then
#        curl -fsSL https://get.docker.com/ | sudo sh
#    fi
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $(whoami)
}

# packages to install after others
list_suffix_packages='htop iotop iftop multitail dstat jq python-docker-py'
# list_suffix_packages='htop jq pigz gdisk aria2 python-docker-py'

# script to run for installing suffix_packages
in_suffix_packages() {
    in_repo_pkg "$list_suffix_packages"

    # Install Rocker
    curl -fsSL ${rocker_artifact_url} \
    | sudo tar -xzC /usr/local/bin && sudo chmod +x /usr/local/bin/rocker
}

# packages to install if a VM
list_vm_packages='dkms qemu-guest-agent open-vm-tools'

# command to run for installing vm_packages
in_vm_packages() {
    in_repo_pkg "$list_vm_packages"
    # return 0
}

# command to install one or more os package manager package
in_repo_pkg() {
    retry_with_timeout 10 300 sudo yum -y install $*
}

rm_repo_pkg() {
    retry_with_timeout 10 300 sudo yum -y autoremove $*
}

# command to update all packages in the os package manager
up_repo_pkg_all() {
    retry_with_timeout 10 300 sudo yum -y update
}

# command to rebuild the os package manager's database
up_repo_db() {
    retry_with_timeout 10 300 sudo yum -y makecache
}

# command to set os package manager proxy
set_repo_proxy_conf() {
    sudo sed -i -e '/^proxy=/d' /etc/yum.conf
    echo "proxy=${http_proxy}" \
        | append /etc/yum.conf
}

# command to set os package manager to keep its cache
set_repo_keepcache_conf() {
    sudo sed -i -e '/^keepcache=/d' /etc/yum.conf
    echo "keepcache=1" \
        | append /etc/yum.conf
}

# idempotent config script to fixup repos to properly use proxycaches
set_repo_cacheable_idempotent() {
    sudo sed -i -e 's/^#baseurl=/baseurl=/' /etc/yum.repos.d/*
    sudo sed -i -e 's/^mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/*
}

set_repo_mirror_idempotent() {
    # sudo sed -i -e "s#http:///centos#http://${mirror_val}/centos#g" /etc/yum.repos.d/*
    sudo sed -i -e "s#http://.*/centos#http://${mirror_val}/centos#g" /etc/yum.repos.d/*
}

# command to set the proxy for the whole OS
set_os_proxy() {
    sudo sed -i -e '/_proxy/d' /etc/environment
    echo -n "http_proxy=${http_proxy}\nhttps_proxy=${http_proxy}\nftp_proxy=${http_proxy}\n" \
        | append /etc/environment
    if $mirror_flag; then
        echo -n "no_proxy=${mirror_val}\n" | append /etc/environment
    fi
}

# command to determine if the OS needs restarting after package updates
get_os_needs_restarting() {
    if ! [ -z "$(sudo /usr/bin/needs-restarting)" ]; then
        return 0
    else
        return 1
    fi
}

# command to reboot the system
do_reboot() {
    sudo reboot
}

# Command to configure docker's proxy under centos flavored systemd
set_docker_proxy() {
    local tmpconf="/etc/systemd/system/docker.service.d/http-proxy.conf"
    if ! [ -d "$(dirname $tmpconf)" ]; then
        sudo mkdir "$(dirname $tmpconf)"
    fi
    log "sed error is OK here if the proxy config file does not yet exist."
    sudo sed -i -e '/HTTP_PROXY/d' "$tmpconf"
    echo "Environment=\"HTTP_PROXY=${http_proxy}\" \"NO_PROXY=localhost,127.0.0.1,$(hostname),$(hostname -f)\"" \
        | append "$tmpconf"
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    sudo systemctl status docker
}

# command to add mitm cert to docker trust store
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
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    sudo systemctl status docker
}

# command to add mitm cert to local trust store
set_mitm_cert() {
    sudo cp "${1}" "/etc/pki/ca-trust/source/anchors/$(basename ${1}).crt"
    sudo update-ca-trust extract
}

do_post_install() {
    # Disable postfix since we don't need an MTA
    sudo systemctl disable --now postfix
}

override_dhcp_dns() {
    nameserver_list="${1}"
    sudo sed -i -e 's/PEERDNS="yes"/PEERDNS="no"/' /etc/sysconfig/network-scripts/ifcfg-*
    sudo sed -i -e '/DNS[0-9]=/d' /etc/sysconfig/network-scripts/ifcfg-*
    sudo sed -i -e '/nameserver/d' /etc/resolv.conf
    nsnumber=1
    for nameserver in $(echo ${nameserver_list} | tr ',' ' '); do
        echo "nameserver ${nameserver}" | append /etc/resolv.conf
        for script in /etc/sysconfig/network-scripts/ifcfg-*; do
            echo "DNS${nsnumber}=${nameserver}" | append "${script}"
        done
        nsnumber=$((nsnumber++))
    done
}
