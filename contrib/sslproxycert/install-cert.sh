#!/usr/bin/env bash

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.


if [[ $EUID -ne 0 ]]; then
   echo "You must run $0 as root:" 1>&2
   echo "\$ sudo $0 <cert_file>" 1>&2
   echo "default is 'emc_ssl.pem'" 1>&2
   exit 1
fi

cert=${1:-"emc_ssl.pem"}

detect_os() {

    # detect Ubuntu and anything using LSB
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

    # output
    echo "$os"
}

###
case "$(detect_os)" in

    rhel*|centos*)
        cp "$cert" "/etc/pki/ca-trust/source/anchors/${cert}.crt"
        update-ca-trust extract
        ;;

    debian*|ubuntu*)
        cp "$cert" "/usr/local/share/ca-certificates/${cert}.crt"
        update-ca-certificates
        ;;

    *)
        echo "Auto install is not supported on this OS: $os"
        ;;
esac

echo "Reminder: restart any processes (eg. Docker) that depend on the local trust store."
