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


### Usage
# TODO: Add GitHub URLs to help text (bottom)
usage() {
    log "providing usage info"
cat <<EOH | more
[Usage]
 -h, --help
    Display this help text and exit
 --help-build
    Display build environment help and exit
 --version
    Display version information and exit

[General Options]
 -y / -n
    Assume YES or NO to any questions (may be dangerous).
 -v / -q
    Be verbose (also show all logs) / Be quiet (only show necessary output)
 -c <FILE>
    If you have a deploy.yml ready to go, give its path to this arg.

[Platform Options]
 --ssh-private-key <id_rsa | id_ed25519>
 --ssh-public-key <id_rsa.pub | id_ed25519.pub>
    Import SSH public key auth material and use it when authenticating to remote nodes.
 -o, --override-dns <NS1,NS2,NS*>
    Override DHCP-configured nameserver(s); use these instead. No spaces! Use of -o is deprecated, please use --override-dns.
 -g, --vm-tools
    Install virtual machine guest agents and utilities for QEMU and VMWare. VirtualBox is not supported at this time. Use of -g is deprecated, please use --vm-tools.
 -m, --centos-mirror <URL>
    Use the provided package <mirror> when fetching packages for the base OS (but not 3rd-party sources, such as EPEL or Debian-style PPAs). The mirror is specified as '<host>:<port>'. This option overrides any mirror lists the base OS would normally use AND supersedes any proxies (assuming the mirror is local), so be warned that when using this option it's possible for bootstrapping to hang indefinitely if the mirror cannot be contacted. Use of -m is deprecated, please use --centos-mirror.

[Docker Options]
 -r, --registry-endpoint REGISTRY
    Use the Docker registry at REGISTRY instead of DockerHub. The connect string is specified as '<host>:<port>[/<username>]'. You may be prompted for your credentials if authentication is required. You may need to use -d (below) to add the registry's cert to Docker. Use of -r is deprecated, please use --registry-endpoint.

 -l, --registry-login
    After Docker is installed, login to the Docker registry to access images which require access authentication. This will authenticate with Dockerhub unless --registry-endpoint is also used. Use of -l is deprecated, please use --registry-login.

 -d, --registry-cert <FILE>
    [Requires --registry-endpoint] If an alternate Docker registry was specified with -r and uses a cert that cannot be resolved from the anchors in the local system's trust store, then use -d to specify the x509 cert file for your registry.

[Proxies & Middlemen]
 -p, --proxy-endpoint <PROXY>
    Connect to the Internet via the PROXY specified as '[user:pass@]<host>:<port>'. Items in [] are optional. It is assumed this proxy handles all protocols.  Use of -p is deprecated, please use --proxy-endpoint.
 -k, --proxy-cert <FILE>
    Install the certificate in <file> into the local trust store. This is useful for environments that live behind a corporate HTTPS proxy.  Use of -k is deprecated, please use --proxy-cert.
 -t, --proxy-test-via <HOSTSPEC>
    [Requires --proxy-endpoint] Test Internet connectivity through the PROXY by connecting to HOSTSPEC. HOSTSPEC is specified as '<host>:<port>'. By default 'google.com:80' is used. Unless access to Google is blocked (or vice versa), there is no need to change the default.

[Examples]
 Install VM guest agents and use SSH public key auth keys in the .ssh/ directory.
    $ bash bootstrap.sh --vm-tools --ssh-private-key .ssh/id_rsa --ssh-public-key .ssh/id_rsa.pub

 Quietly use nlanr.peer.local on port 80 and test the connection using EMC's webserver.
    $ bash bootstrap.sh -q --proxy-endpoint nlanr.peer.local:80 -proxy-test-via emc.com:80

 Assume YES to all questions. Use the CentOS mirror at http://cache.local/centos when fetching packages. Use the Docker registry at registry.local:5000 instead of DockerHub, and install the x509 certificate in certs/reg.pem into Docker's trust store so it can access the Docker registry.
    $ bash bootstrap.sh -y --centos-mirror http://cache.local/centos --registry-endpoint registry.local:5000 --registry-cert certs/reg.pem

For additional information, read the docs on GitHub.
For additional help, please open an issue on GitHub.

EOH
}


### Usage for Build Commands
usage_build() {
    log "providing usage info"
cat <<EOH | more
[Usage]
 -h, --help
    Display this help text and exit
 --help-build
    Display build environment help and exit
 --version
    Display version information and exit

[Build Options]
 --zero-fill-ova
    Reduce ephemera, defrag, and zerofill the instance after bootstrapping
 --build-from <URL>
    Use the Alpine Linux mirror at <URL> to build the ecs-install image locally.
    Mirror list: https://wiki.alpinelinux.org/wiki/Alpine_Linux:Mirrors

For additional information, read the docs on GitHub.
For additional help, please open an issue on GitHub.

EOH
}


##### Boilerplate ############################################################
# The build environment is always determined by the last bootstrap.sh run
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
lib="${root}/ui/libexec"
plugins="${root}/bootstrap_plugins"
cd "${root}"
#
# Save installation root to user's home directory and make it available
# in this script's shell context
echo "INSTALL_ROOT=${root}" >$HOME/.ecsinstallrc
export INSTALL_ROOT="${root}"
#
source "${lib}/includes.sh"
#
##############################################################################

os=''
noargs=false
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
dlogin_flag=false
regcert_flag=false
regcert_val=''
vm_flag=false
verbose_flag=false
quiet_flag=false
minimal_flag=false
docker_flag=false
deploy_flag=false
deploy_val=''
dhcpdns_flag=false
dhcpdns_val=''
hello_image='hello-world'
os_supported=false
alpine_mirror=''
mirror_flag=false
mirror_val=''
zerofill_flag=false
ssh_private_key_flag=false
ssh_private_key_val=''
ssh_public_key_flag=false
ssh_public_key_val=''


### Version String
version() {
    o " ${release_name} Install Node Bootstrap ${ver_maj}.${ver_min}.${ver_rev}${ver_tag}"
    o " ${release_product} Image ${release_artifact}:${release_tag}"
}


### Argue with arguments
# Switched to util-linux getopt so we can use long form arguments

if [ -z "$1" ]; then
    noargs=true
fi

if ! O=$(
         getopt \
         -l build-from:,deploy-config:,registry-cert:,help,help-build,proxy-cert:,registry-login,centos-mirror:,override-dns:,proxy-endpoint:,registry-endpoint:,proxy-test-via:,vm-tools,zero-fill-ova,ssh-private-key:,ssh-public-key:,version,help-build,yes,no,verbose,quiet \
         -o c:d:hk:lm:no:r:t:p:gyvqz \
         -n "${0}" \
         -- ${@}
        ); then
    usage
    exit 1
fi

eval set -- "${O}"

while true; do
  case "${1}" in
# Usage
    -h|--help)
        usage
        exit 1
        ;;
    --help-build)
        usage_build
        exit 1
        ;;
    --version)
        shift
        version
        exit 0
        ;;
# General
    -y|--yes)
        export override_flag=true
        export override_val=true
        shift
        ;;
    -n|--no)
        export override_flag=true
        export override_val=false
        shift
        ;;
    -v|--verbose)
        export verbose_flag=true
        export quiet_flag=false
        shift
        ;;
    -q|--quiet)
        export quiet_flag=true
        export verbose_flag=false
        shift
        ;;
# Configuration
    -c|--deploy-config)
        export deploy_flag=true
        export deploy_val="${2}"
        ensure_file_exists "${deploy_val}" "ecs-install deployment file: not found"
        shift 2
        ;;
    --ssh-private-key)
        export ssh_private_key_flag=true
        export ssh_private_key_val="${2}"
        ensure_file_exists "${ssh_private_key_val}" "SSH private key file"
        ensure_string_list_matches id_rsa,id_ed25519 "${ssh_private_key_val}" "SSH private key file: bad name"
        shift 2
        ;;
    --ssh-public-key)
        export ssh_public_key_flag=true
        export ssh_public_key_val="${2}"
        ensure_file_exists "${ssh_public_key_val}" "SSH public key file: not found"
        ensure_string_list_matches id_rsa.pub,id_ed25519.pub "${ssh_public_key_val}" "SSH public key file: bad name"
        shift 2
        ;;
    -m|--centos-mirror)
        export mirror_flag=true
        export mirror_val="${2}"
        shift 2
        ;;
    -o|--override-dns)
        export dhcpdns_flag=true
        export dhcpdns_val="${2}"
        shift 2
        ;;
    -g|--vm-tools)
        export vm_flag=true
        shift
        ;;
# HTTP Proxy
    -p|--proxy-endpoint)
        export proxy_flag=true
        export proxy_val="${2}"
        shift 2
        ;;
    -k|--proxy-cert)
        export mitm_flag=true
        export mitm_val="${2}"
        ensure_file_exists "${mitm_val}" "HTTPS proxy cert: not found"
        shift 2
        ;;
    -t|--proxy-test-via)
        export proxy_test_flag=true
        export proxy_test_val="${2}"
        shift 2
        ;;
# Docker Registry
    -r|--registry-endpoint)
        export registry_flag=true
        export registry_val="${2}"
        shift 2
        ;;
    -l|--registry-login)
        export dlogin_flag=true
        shift
        ;;
    -d|--registry-cert)
        export regcert_flag=true
        export regcert_val="${2}"
        ensure_file_exists "${regcert_val}" "Docker registry cert: not found"
        shift 2
        ;;
# Build Tools
    --zero-fill-ova)
        export zerofill_flag=true
        shift
        ;;
    --build-from)
        export build_image_flag=true
        export alpine_mirror="${2}"
        ensure_string_matches http "${alpine_mirror}" "Requested build, but invalid APK mirror provided"
        shift 2
        ;;
    --)
        shift
        break
        ;;
    *)
        shift
        #usage
        die "Invalid option: ${1} in {${*}}"
        ;;
  esac
done


### Post Argparse Validation
if ${ssh_private_key_flag} || ${ssh_public_key_flag}; then
    if ! ( $ssh_private_key_flag && $ssh_public_key_flag ); then
        die "You must specify both an SSH private key file and an SSH public key file."
    fi
fi


##############################################################################
### Main
o ""
version
o "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


### No arguments given.. are you sure?
if ${noargs}; then
    o ""
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
dump_bootstrap_config >"${root}/bootstrap.conf"


### Auth
o ""
o "Escalating privileges"
o "    You may be presented with the system sudo banner and asked"
o "    for your password depending on the Linux flavor and default"
o "    sudo configuration for your system."
o ""
ping_sudo || die "Unable to escalate using sudo."


### Import vars for this specific OS
o ""
p Detecting OS
source "${plugins}/plugin-defaults.plugin.sh"
source "${plugins}/os-router.plugin.sh"
detect_os
route_os
o "Environment is $os"
o "    [supported: ${os_supported}]"
o ""


### Collect info
o "We collect some hardware and OS info into a log file on the"
o "install node in case something fails and you want help trouble-"
o "shooting. HOWEVER, absolutely nothing is transmitted over the"
o "Internet or shared with EMC, GitHub, or anyone else unless or"
o "until you decide to attach the log file or copy & paste its"
o "content into a help request on GitHub (or where ever)."
o ""
o "If you are curious to see what's collected, the log is here:"
o "    ${log_file}"
o ""
o "It is perfectly fine to remove this log file at any time."
o ""
p Collecting system info
collect_environment_info


###
o "Onward to bootstrapping.  This can take anywhere between five"
o "minutes to a few hours depending on many factors, the most"
o "important being the speed of your Internet connection."
o "The ECS software docker image is around 1.5GiB."
o "Bootstrapping requires about 10 minutes under KVM on a"
o "Xeon E5 with a 250Mbps Internet connection."
o ""


### Set utility symlinks in current user's path for various callables
v "Creating shell shims in ${HOME}/bin for CLI commands"
p Installing CLI shims
symlink_scripts
update_path_in_bashrc


### Create install tree
v "Creating install tree"
p Create install tree
create_install_tree


### Override nameservers provided by DHCP if -o was given.
if ${dhcpdns_flag}; then
    v "Overriding DHCP nameservers"
p Overriding DHCP nameservers
    override_dhcp_dns "${dhcpdns_val}"
fi


### Do we need to do a MitM cert?
if ${mitm_flag}; then
    v "Adding ${mitm_val} to the local trust store and installer queue"
p Installing proxy cert
    set_mitm_cert "$mitm_val"
    if ! [ -d "${docker_host_root}/ssl" ]; then
        sudo mkdir -p "${docker_host_root}/ssl"
    fi
    sudo cp "$mitm_val" "${docker_host_root}/ssl/sslfw.pem"
fi


### If we got proxies then set them up in the local shell
### and the system environment settings
if ${proxy_flag}; then
    v "Checking connectivity through proxy ${proxy_val}"
p Checking proxy connection
    proxy_http_ping "${proxy_val}" "${proxy_test_val}" 2>&1 >/dev/null
    if [ $? -gt 0 ]; then
        v " failed!"
        die "Could not form CONNECT to '${proxy_test_val}' with provided proxy string"
    else
        v "Connectivity OK!"
    fi
    v "Configuring system for proxy ${proxy_val}"
p Setting system proxy
    export http_proxy="http://${proxy_val}"
    export https_proxy="https://${proxy_val}"
    export ftp_proxy="ftp://${proxy_val}"
    if ${mirror_flag}; then
        export no_proxy="${mirror_val}"
    fi
    set_os_proxy || die "Couldn't write to /etc/environment"
    # set package manager proxy in package manager config
    # Set docker proxy after installing it
fi


### Refresh sudo timestamp
ping_sudo


### Configure system package manager repos for proxies
if ${proxy_flag} && ! ${mirror_flag}; then
    v "Configuring system package manager for proxies"
p Setting package manager proxy
    set_repo_proxy_conf
    set_repo_cacheable_idempotent
fi


### Configure system package manager repos for mirror
if ${mirror_flag}; then
    v "Configuring system package manager mirror"
p Setting package manager mirror
    set_repo_cacheable_idempotent
    set_repo_mirror_idempotent
fi


### Configure system package manager to keep its cache
### This is so we can reuse it later for nodes
v "Configuring system package manager to keep its cache so it can be used for other nodes"
p Setting package manager keepcache
set_repo_keepcache_conf


### Preflight cleaning
v "Performing preflight checklist"
p Performing preflight checklist
do_preflight 2>&1 | log
ping_sudo


### Update repo databases and all system packages
v "Updating system package manager databases pass (1/2)"
p Updating package manager database
up_repo_db 2>&1 | log
ping_sudo


v "Updating all system packages pass (1/2)"
p Updating installed packages
up_repo_pkg_all 2>&1 | log
ping_sudo


###
o "This script installs all packages that are both required for"
o "the deployment and that we think will be helpful to you when"
o "managing and operating your environment."
o ""


### Do system package installs
v "Installing bootstrap packages pass (1/3)"
p Installing new packages
in_prefix_packages 2>&1 | log
ping_sudo


p Installing packages
v "Installing bootstrap packages pass (2/3)"
p Installing new packages
in_general_packages 2>&1 | log
ping_sudo


p Installing packages
v "Installing bootstrap packages pass (3/3)"
p Installing new packages
in_suffix_packages 2>&1 | log
#if $proxy_flag; then
#    set_repo_proxy_idempotent
#fi
ping_sudo


### Do we need VM guest additions?
if ${vm_flag}; then
    v "Installing virtual machine guest additions"
p Installing VM guest additions
    in_vm_packages 2>&1 | log
#    if $proxy_flag; then
#        set_repo_proxy_idempotent
#    fi
    ping_sudo
fi

### Lock packages that we don't want updated
v "Locking packages we don't want updated"
p locking docker packages
versionlock_packages 2>&1 | log
ping_sudo

### Update repo databases and all system packages (again)
### This will pick up any updates pulled in from alternate repos.
v "Updating system package manager databases pass (2/2)"
p Updating package manager database
up_repo_db 2>&1 | log
ping_sudo


v "Updating all system packages pass (2/2)"
p Updating installed packages
up_repo_pkg_all 2>&1 | log
ping_sudo


###
o "We're going to start working with Docker now. If you elected"
o "to build your own ecs-install image rather than pull one from"
o "the EMC Dockerhub repo, it will add some time to your initial"
o "bootstrap."
o ""


### If Docker needs proxy configs, do that now.
if ${proxy_flag}; then
    v "Configuring Docker proxy settings"
p Setting Docker proxy
    set_docker_proxy 2>&1 | log
    ping_sudo
fi


### If Docker needs to use a custom registry, set that up now.
docker_registry
ping_sudo


###
v "Check if Docker login needed"
if ${dlogin_flag}; then
    retry_until_ok docker login
fi


### Test Docker install
v "Testing docker installation"
p Testing Docker
if docker_test; then
    v "Docker was installed correctly"
else
    error "Docker test did not pass. Try running the following command"
    error "and check the output for errors:"
    error ""
      die "\$ sudo docker run --rm ${hello-image}"
fi
ping_sudo


### Run post-install
v "Running post-install scripts for ${os}"
p Post-install scripts
do_post_install 2>&1 | log
ping_sudo


### Create host paths
v "Creating host paths"
p Creating host paths
for directory in "${docker_host_root}/ssl" "${docker_host_root}/ssh" "${docker_host_logs}"; do
    if ! [ -d "${directory}" ]; then
        sudo mkdir -p "${directory}"
    fi
done
for directory in "${docker_host_root}/ssl" "${docker_host_root}/ssh"; do
    sudo chmod 0700 "${directory}"
done


### Copy existing deploy.yml
if ${deploy_flag}; then
v "Copying deploy.yml"
p Copying deploy.yml
    sudo cp "${deploy_val}" "${docker_host_root}/deploy.yml"
fi


### Copy existing SSH public/private keys
if ${ssh_private_key_flag} && ${ssh_public_key_flag}; then
v "Copying SSH public and private keys"
p Copying SSH keys
    sudo cp "${ssh_private_key_val}" "${ui_host_ssh_dir}/$(basename ${ssh_private_key_val})"
    sudo cp "${ssh_public_key_val}" "${ui_host_ssh_dir}/$(basename ${ssh_public_key_val})"
fi


### ECS-Install Docker image
if ${build_image_flag}; then
p Building ecs-install image
    if ! ui/build_image.sh 2>&1 | log; then
        error "We couldn't build the ecs-install image for some reason. Please check the logs."
        error "If it's something simple, such as a missing base image (we use python:2.7-alpine),"
        error "then you may be able to get the image to build by pulling python:2.7-alpine from"
        error "a reliable source, such as DockerHub. If you specified a custom registry, then you"
        error "may need to first push the image into your registry to ensure it is available for"
        error "the build tool."
        die "If you still need more help after trying the above, you can reach us on GitHub."
    fi
else
    p Pulling ecs-install image
    if ! ui/pull_image.sh 2>&1 | log; then
        error "We couldn't pull the ecs-install image for some reason. Please check the logs."
        error "If it's something simple, such as the ecs-install:latest image missing from"
        error "your custom Docker registry, or if your Internet access isn't working, then"
        error "you may be able to solve the problem by first solving one of the above issues."
        die "If you still need more help after trying the above, you can reach us on GitHub."
    fi
fi
ping_sudo


###
o "We are now pulling the ${release_artifact} image."
o "This can take quite a long time over a slow Internet link or"
o "if the backing block storage system is slower than usual."
o ""


### ECS Docker Image
v "Pulling ${release_artifact}:${release_tag} Docker image"
p Pulling ECS-Software image
if ${registry_flag}; then
    if ! sudo docker pull ${registry_val}/${release_artifact}:${release_tag} 2>&1 | log; then
        error "We couldn't pull the software image for some reason. Since you're using a custom"
        error "registry, it may be that the image does not exist in your registry. Please ensure"
        error "the '${release_artifact}' image is present on your registry before trying again, or"
        error "perhaps you can simply pull the image directly from DockerHub."
        die "If you still need more help after trying the above, you can reach us on GitHub."
        # This has to be tagged for the cache generator in Ansible
    fi
    v "Tagging ${registry_val}/${release_artifact}:${release_tag} -> ${release_common_name}"
    sudo docker tag "${registry_val}/${release_artifact}:${release_tag}" "${release_common_name}" 2>&1 | log
else
    if ! sudo docker pull "${release_artifact}:${release_tag}" 2>&1 | log; then
        error "We couldn't pull the software image for some reason. It may be a temporary issue"
        error "or there may be an issue with your Internet access. You'll likely need to check"
        error "the error message from the Docker pull output (above) to see what's specifically"
        error "the problem."
        die "If you still need more help after trying the above, you can reach us on GitHub."
    fi
    v "Tagging ${release_artifact}:${release_tag} -> ${release_common_name}"
    sudo docker tag "${release_artifact}:${release_tag}" "${release_common_name}" 2>&1 | log
fi
ping_sudo


### Log Docker Inventory
v "Logging Docker Inventory"
p Logging Docker Inventory
sudo docker images 2>&1 | log
sudo docker ps -a 2>&1 | log
ping_sudo


### Next steps
p ''
q 'All done bootstrapping your install node.'
o ''
o 'To continue (after reboot if needed):'
o "    $ cd ${root}"
o "If you have a deploy.yml ready to go (and did not use -c flag):"
o '    $ sudo cp deploy.yml /opt/emc/ecs-install/'
o 'If not, check out the docs/design and examples directory for references.'
o 'Once you have a deploy.yml, you can start the deployment'
o 'by running:'
o ''
o '[WITH Internet access]'
o '    $ step1'
o '  [Wait for deployment to complete, then run:]'
o '    $ step2'
o ''
o '[WITHOUT Internet access]'
o '    $ island-step1'
o '  [Migrate your install node into the isolated environment and run:]'
o '    $ island-step2'
o '  [Wait for deployment to complete, then run:]'
o '    $ island-step3'
o ''


### Needs rebooting?
if get_os_needs_restarting; then
    ping_sudo
    q "The system has indicated it wants to reboot."
    o "Please reboot BEFORE continuing to ensure this node is"
    o "operating with the latest kernel and system libraries."
    o ''
    if ${override_flag}; then
        if ${override_val}; then
            q "Automatically rebooting by user request (-y argument)"
            log "REBOOT-REBOOTING-ARGUMENT"
            wait_bar 15 "Press CTRL-C to abort"
            do_reboot
        else
            q "Skipping reboot by user request (-n argument)"
            log "REBOOT-SKIPPED-ARGUMENT"
        fi
    else
        ask "Would you like to reboot now?"
        if [ $? -eq 0 ]; then
            log "REBOOT-REBOOTING-INTERACTIVE"
            do_reboot
        else
            log "REBOOT-SKIPPED-INTERACTIVE"
            q "Skipping reboot by user request"
        fi
        log "END-ASK-REBOOT"
    fi
fi

if ${zerofill_flag}; then
    sudo bash "${INSTALL_ROOT}/tools/zerofill.sh"
fi


### finish up and reset sudo timestamp
quit_sudo
exit 0
