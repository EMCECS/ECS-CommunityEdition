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

############################################################################
# This script should be run on a fresh, minimal install of a supported OS. #
# It will attempt to build up a baseline operating environment for the     #
# installer system.                                                        #
############################################################################

### How to
# TODO: Add github URLs to help text (bottom)
usage() {
    log "providing usage info"
cat <<EOH

[Usage]
 -h             This help text

[General Options]
 -y / -n        Assume YES or NO to any questions (may be dangerous).

 -v             Install virtual machine guest agents and utilities for QEMU and VMWare.
                VirtualBox is not supported at this time.

[Docker Options]
 -r <registry>  Use the Docker registry at <registry> instead of DockerHub.
                The connect string is specified as '<host>:<port>[/<username>]'
                You may be prompted for your credentials if authentication is required.
                You may need to use -d (below) to add the registry's cert to Docker.

 -d <x509.crt>  NOTE: This does nothing unless -r is also given.
                If an alternate Docker registry was specified with -r and uses a cert
                that cannot be resolved from the anchors in the local system's trust
                store, then use -d to specify the x509 cert file for your registry.

[Proxies & Middlemen]
 -k <x509.crt>  Install the certificate in <file> into the local trust store. This is
                useful for environments that live behind a corporate HTTPS proxy.

 -p <proxy>     Use the <proxy> specified as '[user:pass@]<host>:<port>'
                items in [] are optional. It is assumed this proxy handles all protocols.

 -t <connect>   Attempt to CONNECT through the proxy using the <connect> string specified
                as '<host>:<port>'. By default 'google.com:80' is used. Unless you block
                access to Google (or vice versa), there's no need to change the default.

[Examples]
 Install VM guest agents and install the corporate firewall cert in certs/mitm.pem.
    $ bash bootstrap.sh -v -k certs/mitm.pem

 Use nlanr.peer.local on port 80 and test the connection using EMC's webserver.
    $ bash bootstrap.sh -p nlanr.peer.local:80 -t emc.com:80

 Assume YES to all questions and use the proxy cache at cache.local port 3128 for HTTP-
 related traffic. Use the Docker registry at registry.local:5000 instead of DockerHub,
 and install the x509 certificate in certs/reg.pem into Docker's trust store so it can
 access the Docker registry.
    $ bash bootstrap.sh -y -p cache.local:3128 -r registry.local:5000 -d certs/reg.pem

For additional information, read the docs on GitHub.
For additional help, please open an issue on GitHub.

EOH
}

##### Boilerplate ############################################################
# The build environment is always determined by the last bootstrap.sh run
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
lib=${root}/ui/lib
cd $root
#
# Save installation root to user's home directory and make it available
# in this script's shell context
echo "INSTALL_ROOT=${root}" >$HOME/.ecsinstallrc
export INSTALL_ROOT="${root}"
#
# DEPRECATED: shell-style environment flags are deprecated and will be replaced
# DEPRECATED: by new context system, but some scripts still depend on these.
DRONE=${DRONE:-false}
BUILD=${BUILD:-false}
MONITOR=${DRONE:-false}
#
# Imports and import configs
release_name="ECS Community Edition"
release_version="2.2.1"
release_artifact="emccorp/ecs-software-2.2:latest"
log_file="/dev/null"
log() {
    if [ -z "$*" ]; then
        while read -r line; do
            printf "%s\n" "${line}" >> "${log_file}"
        done
    else
        printf "%s\n" "${*}" >> "${log_file}"
    fi
}

# generic output formatter
o() {
    printf "> %s\n" "${*}"
    log "> [$0] ${*}"
}

# generic warning formatter
warn() {
    o "WARNING: ${*}"
}

# generic error formatter
error() {
    o "ERROR: ${*}"
}

# generic error formatter with exit 1
die() {
    o "ERROR: ${*}"
    # o "If you believe you have received this in error, please open an issue on github."
    exit 1
}

ask() {
    o "${*}"
    read -p " <y/N> " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

log_file="${root}/ministrap.log"

### Basic OS detection
os=''
detect_os() {


    # detect Ubuntu and anything using lsb_release
    if [ -f /etc/lsb-release ]; then
        os=$(lsb_release -d -s)

    # detect Debian version
    elif [ -f /etc/debian_version ]; then
        os="debian $(cat /etc/debian_version)"

    # detect RHEL, CentOS, and variants
    elif [ -f /etc/redhat-release ]; then
        os=`cat /etc/redhat-release`
    # TODO: SuSE, Arch, etc...

    # fallback for unknowns, perhaps they can be added to the list.
    else
        os="$(uname -s) $(uname -r) $(cat /etc/*_ver* /etc/*-rel*)"
    fi

    # Are we in a container?
    if ! [ -z "$(cut -d':' -f3 /proc/1/cgroup | grep '^/$')" ]; then

        # Detect if we're running under Docker
        if ! [ -z "$(cut -d':' -f3 /proc/1/cgroup | grep '^/docker/.*$')" ]; then
            container_flag=true
            os="docker ${os}"

        # Or perhaps LXC?
        elif ! [ -z "$(cut -d':' -f3 /proc/1/cgroup | grep '^/lxc/.*$')" ]; then
            container_flag=true
            os="lxc ${os}"
        fi

    fi

    # string to lowercase
    os="${os,,}"
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

# The missing privileged file redirection command
append() {
    sudo dd status=none oflag=append conv=notrunc of="${1}"
}

collect_environment_info() {
    if $container_flag; then
        o "Running in a container, skipping collection"
    else

        log "GET-HWINFO"
        sudo dmesg 2>&1 | log
        log "END-DMESG"
        sudo uname -a 2>&1 | log
        log "END-UNAME"
        sudo lsmod 2>&1 | log
        log "END-LSMOD"
        sudo lscpu 2>&1 | log
        log "END-LSCPU"
        sudo lspci 2>&1 | log
        log "END-LSPCI"
        sudo lsscsi 2>&1 | log
        log "END-LSSCSI"
        sudo lsusb 2>&1 | log
        log "END-LSUSB"
        sudo lshw 2>&1 | log
        log "END-LSHW"
        sudo hwinfo 2>&1 | log
        log "END-HWINFO"
        sudo dmidecode 2>&1 | log
        log "END-DMIDECODE"
        sudo free -h 2>&1 | log
        log "END-FREE"
        sudo df -h 2>&1 | log
        log "END-DF"
        sudo mount 2>&1 | log
        log "END-MOUNT"
        sudo fdisk -l 2>&1 | log
        log "END-FDISK"
        sudo parted -l 2>&1 | log
        log "END-PARTED"
        sudo pvs 2>&1 | log
        log "END-PVS"
        sudo gvs 2>&1 | log
        log "END-GVS"
        sudo lvs 2>&1 | log
        log "END-LVS"
        log "END-COLLECT-ENVIRONMENT-INFO"
    fi
}

proxy_http_ping() {

    echo "curl -sSLfI -w '%{http_code}' -x ${1} --proxytunnel ${2} -o /dev/null -m 10" | log
    curl -sSLfI -w '%{http_code}' -x ${1} --proxytunnel ${2} -o /dev/null -m 10
    return ${?}
}

ping_sudo() {
    sudo -v
}

quit_sudo() {
    sudo -k
}

dump_bootstrap_config() {
    _vars="override_flag override_val mitm_flag mitm_val proxy_flag proxy_val proxy_test_flag proxy_test_val"
    _vars="$_vars build_image_flag registry_flag registry_val regcert_flag regcert_val vm_flag docker_flag"
    _vars="$_vars DEVEL DRONE BUILD INSTALL_ROOT"
    for _var in $_vars; do
        eval echo "export $_var=\$$_var"
    done
}


docker_test() {
    docker_hello=$(sudo docker run --rm ${hello_image} 2>&1)
    if [ -z "${docker_test##*'Hello from Docker'*}" ]; then
        return 0
    else
        return 1
    fi
}

docker_registry() {
    if $registry_flag; then
        hello_image="${registry_val}/hello-world"
        if $regcert_flag; then
            set_docker_reg_cert "${registry_val}" "${regcert_val}" 2>&1 | log
            if ! [ -d /opt/emc/ssl ]; then
                sudo mkdir -p "${docker_host_root}/ssl"
            fi
            sudo cp "${regcert_val}" "${docker_host_root}/ssl/docker.pem"
        fi
    else
        hello_image="hello-world"
    fi
}

docker_clean() {
    o "Cleaning up... "

    o "[exited and data-only containers] "
    if ! [ -z "$(docker ps -q -f status=exited)" ]; then
        sudo docker rm -vf $(docker ps -q -f status=exited)
    fi

    o "[dangling layers] "
    if ! [ -z "$(docker images -q --filter "dangling=true")" ]; then
        sudo docker rmi $(docker images -q --filter "dangling=true")
    fi
    o "done."
}

data_container_missing() {
    [ -z "$(sudo docker ps -a | grep ecs-install-data)" ]
}

make_new_data_container() {
    o "Creating new data container"
    sudo docker run -d --name "${data_container_name}" \
        --entrypoint /bin/echo ${latest_image_path} \
        echo "Data container for ecs-install" >/dev/null
}
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

# packages to install before others
list_prefix_packages='epel-release python-devel wget curl ntp'

# script to run for installing prefix_packages
in_prefix_packages() {
    in_repo_pkg "$list_prefix_packages"
}

# packages to install
list_general_packages='yum-utils git python-pip python-docker-py'

# script to run for installing general_packages
in_general_packages() {
    in_repo_pkg "$list_general_packages"
    pip install --upgrade pip
}

# packages to install after others
list_suffix_packages='vim htop iotop iftop jq rsync'

# script to run for installing suffix_packages
in_suffix_packages() {
    in_repo_pkg "$list_suffix_packages"

    # Install Rocker
    curl -fsSL https://github.com/grammarly/rocker/releases/download/1.1.2/rocker-1.1.2-linux_amd64.tar.gz \
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
    sudo yum -y install $*
}

# command to update all packages in the os package manager
up_repo_pkg_all() {
    sudo yum -y update
}

# command to rebuild the os package manager's database
up_repo_db() {
    while ! sudo yum -y makecache; do
        sleep 10
        # retry
    done
}

# command to set os package manager proxy
set_repo_proxy_conf() {
    sudo sed -i -e '/^proxy=/d' /etc/yum.conf
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
    echo -n "http_proxy=${http_proxy}\nhttps_proxy=${http_proxy}\nftp_proxy=${http_proxy}\n" \
        | append /etc/environment
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

#
##############################################################################

os=''
override_flag=false
override_val=false
mitm_flag=false
mitm_val=''
proxy_flag=false
proxy_val=''
proxy_test_flag=false
proxy_test_val="google.com:80"
build_image_flag=false
registry_flag=false
registry_val=''
regcert_flag=false
regcert_val=''
vm_flag=false
minimal_flag=false
docker_flag=false
hello_image='hello-world'
os_supported=false


### Route by detected OS
route_os() {

    case "${os}" in

        centos\ linux\ release\ 7.2*)
            :
            #included
            ;;

        # Die on unknowns
        *)
            die "OS unknown and not supported: $os"
            ;;
    esac
}


##############################################################################
### Main
o ""
o " ${release_name} ${release_version} Ministrap for installer 1.0"
o "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


### Argue with arguments
while getopts ":bzynvhp:k:t:d:r:" opt; do
  case $opt in
    d)
        export regcert_flag=true
        export regcert_val="${OPTARG}"
        ensure_file_exists "${regcert_val}" "Docker registry cert"
        ;;
    h)
        usage
        exit 1
        ;;
    k)
        export mitm_flag=true
        export mitm_val="${OPTARG}"
        ensure_file_exists "${mitm_val}" "HTTPS proxy cert"
        ;;
    n)
        export override_flag=true
        export override_val=false
        ;;
    p)
        export proxy_flag=true
        export proxy_val="${OPTARG}"
        ;;
    r)
        export registry_flag=true
        export registry_val="${OPTARG}"
        ;;
    t)
        export proxy_test_flag=true
        export proxy_test_val="${OPTARG}"
        ;;
    v)
        export vm_flag=true
        ;;
    y)
        export override_flag=true
        export override_val=true
        ;;
    \?)
        usage
        die "Invalid option: -$OPTARG"
        ;;
    :)
        usage
        die "Option -$OPTARG requires an argument."
        ;;
  esac
done


### No arguments given.. are you sure?
if [ -z "$1" ]; then
    o "No options were given, but it's possible your environment may"
    o "depend on one or more options to bootstrap properly."
    o ""
    ask "Are you sure you want to continue with the defaults?"
    if [ $? -eq 0 ]; then
        log "ASK-NOARGS-YES-INTERACTIVE"
        o "Continuing with the defaults..."
    else
        log "ASK-NOARGS-NO-INTERACTIVE"
        o "Alright then, here's the options available:"
        usage
        exit 1
    fi
    log "END-ASK-NOARGS"
fi


### Dump config
dump_bootstrap_config >${root}/bootstrap.conf


### Auth
o ""
o "Escalating privileges"
o "     You may be presented with the system sudo banner and asked for your password,"
o "     depending on the Linux flavor and default sudo configuration for your system."
o ""
ping_sudo || die "Unable to escalate using sudo."


### Import vars for this specific OS
detect_os
route_os
o "Environment is $os [supported: ${os_supported}]"
o ""


### Collect info
o "Collecting hardware and OS info in case of future troubleshooting"
o ""
o "NOTE: Nothing is transmitted or shared with EMC, github, or anyone"
o "      else unless you choose to attach files or copy/paste content"
o "      into a github or EMC support issue."
o ""
o "      If you are curious to see what's collected, the log is here:"
o "      $log_file"
o ""
$minimal_flag || collect_environment_info


### If we got proxies then set them up in the local shell
### and the system environment settings
if $proxy_flag; then
    o "Checking connectivity through proxy ${proxy_val}"
    proxy_http_ping "${proxy_val}" "${proxy_test_val}" 2>&1 >/dev/null
    if [ $? -gt 0 ]; then
        o " failed!"
        die "Could not form CONNECT to '${proxy_test_val}' with provided proxy string."
    else
        o "Connectivity OK!"
    fi
    o "Configuring system for proxy ${proxy_val}"
    export http_proxy="http://${proxy_val}"
    export https_proxy="https://${proxy_val}"
    export ftp_proxy="ftp://${proxy_val}"
    set_os_proxy || die "Couldn't write to /etc/environment"
    # set package manager proxy in package manager config
    # Set docker proxy after installing it
fi


### Do we need to do a MitM cert?
if $mitm_flag; then
    o "Adding ${mitm_val} to the local trust store and installer queue"
    set_mitm_cert "$mitm_val"
    if ! [ -d "${docker_host_root}/ssl" ]; then
        sudo mkdir -p "${docker_host_root}/ssl"
    fi
    sudo cp "$mitm_val" "${docker_host_root}/ssl/sslfw.pem"
fi


### Refresh sudo timestamp
ping_sudo


### Configure system package manager repos for proxies
if $proxy_flag; then
    o "Configuring system package manager for proxies"
    set_repo_proxy_conf
    set_repo_proxy_idempotent
fi


### Update repo databases and all system packages
o "Updating system package manager databases pass (1/2)"
up_repo_db 2>&1 | log
ping_sudo

o "Updating all system packages pass (1/2)"
up_repo_pkg_all 2>&1 | log
ping_sudo


### Do system package installs
o "Installing bootstrap packages pass (1/3)"
in_prefix_packages 2>&1 | log
if $proxy_flag; then
    set_repo_proxy_idempotent
fi
ping_sudo

o "Installing bootstrap packages pass (2/3)"
in_general_packages 2>&1 | log
if $proxy_flag; then
    set_repo_proxy_idempotent
fi
ping_sudo

o "Installing bootstrap packages pass (3/3)"
in_suffix_packages 2>&1 | log
if $proxy_flag; then
    set_repo_proxy_idempotent
fi
ping_sudo


### Do we need VM guest additions?
if $vm_flag; then
    o "Installing virtual machine guest additions"
    in_vm_packages 2>&1 | log
    if $proxy_flag; then
        set_repo_proxy_idempotent
    fi
    ping_sudo
fi


### Update repo databases and all system packages (again)
### This will pick up any updates pulled in from alternate repos.
if ! $minimal_flag; then
    o "Updating system package manager databases pass (2/2)"
    up_repo_db 2>&1 | log
    ping_sudo
    o "Updating all system packages pass (2/2)"
    up_repo_pkg_all 2>&1 | log
    ping_sudo
fi


### If Docker needs proxy configs, do that now.
if $proxy_flag; then
    o "Configuring Docker proxy settings"
    set_docker_proxy 2>&1 | log
    ping_sudo
fi


### If Docker needs to use a custom registry, set that up now.
docker_registry
ping_sudo


### Run post-install
o "Running post-install scripts for ${os}"
do_post_install 2>&1 | log
ping_sudo


### Next steps
o 'All done ministrapping the node.'
o ''
o 'To continue (after reboot if needed), come back to this directory and run'
o 'the single- or multi-node installers.'
if $registry_flag; then
o ''
o 'To use your custom registry, be sure to tell the installer script about it'
o 'by adding the following to your command:'
o ''
o "     --imagename ${registry_val}/${release_artifact}"
fi
o ''

if ! $minimal_flag; then
    ### Needs rebooting?
    if get_os_needs_restarting; then

        ping_sudo
        o "The system has indicated it wants to reboot."
        o "Please reboot BEFORE continuing to ensure this node is"
        o "operating with the latest kernel and system libraries."
        o ''

        if $override_flag; then
            if $override_val; then
                o "Automatically rebooting by user request (-y argument)"
                log "REBOOT-REBOOTING-ARGUMENT"
                do_reboot
            else
                o "Skipping reboot by user request (-n argument)"
                log "REBOOT-SKIPPED-ARGUMENT"
            fi
        else
            ask "Would you like to reboot now?"
            if [ $? -eq 0 ]; then
                log "REBOOT-REBOOTING-INTERACTIVE"
                do_reboot
            else
                log "REBOOT-SKIPPED-INTERACTIVE"
                o "Skipping reboot by user request"
            fi
            log "END-ASK-REBOOT"
        fi
    fi
fi


### finish up and reset sudo timestamp
o "All done."
quit_sudo
exit 0
