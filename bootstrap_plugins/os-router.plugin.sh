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

    # string to lowercase
    os="${os,,}"
}

### Route by detected OS
route_os() {

    case "${os}" in

        centos\ linux\ release\ 7.4*)
            source ${plugins}/centos74.plugin.sh
            ;;
        centos\ linux\ release\ 7.5*)
            source ${plugins}/centos75.plugin.sh
            ;;
        centos\ linux\ release\ 7.6*)
            source ${plugins}/centos76.plugin.sh
            ;;
        centos\ linux\ release\ 7.7*)
            source ${plugins}/centos77.plugin.sh
            ;;
        centos\ linux\ release\ 7.8*)
            source ${plugins}/centos78.plugin.sh
            ;;
        centos\ linux\ release\ 7.9*)
            source ${plugins}/centos79.plugin.sh
            ;;
        # Die on unknowns
        *)
            die "OS unknown and not supported: $os"
            ;;
    esac
}
