#@IgnoreInspection BashAddShebang

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# OS detection and routing

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
#    if ! [ -z "$(cut -d':' -f3 /proc/1/cgroup | grep '^/$')" ]; then
#
#        # Detect if we're running under Docker
#        if ! [ -z "$(cut -d':' -f3 /proc/1/cgroup | grep '^/docker/.*$')" ]; then
#            container_flag=true
#            os="docker ${os}"
#
#        # Or perhaps LXC?
#        elif ! [ -z "$(cut -d':' -f3 /proc/1/cgroup | grep '^/lxc/.*$')" ]; then
#            container_flag=true
#            os="lxc ${os}"
#        fi
#
#    fi

    # string to lowercase
    os="${os,,}"
}

### Route by detected OS
route_os() {

    case "${os}" in

#        centos\ linux\ release\ 7.2*)
#            source ${plugins}/centos72.plugin.sh
#            ;;

        centos\ linux\ release\ 7.3*)
            source ${plugins}/centos73.plugin.sh
            ;;

#        dockerized\ centos\ linux\ release\ 7.2*)
#            source ${plugins}/centos72-docker.plugin.sh
#            ;;

        # Die on unknowns
        *)
            die "OS unknown and not supported: $os"
            ;;
    esac
}
