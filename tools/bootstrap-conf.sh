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

if [ -z "${1}" ] || [ -z "${2}" ]; then
    o "Usage:"
    o "${0} KEY VALUE"
    die "Must supply KEY and VALUE."
fi

BOOTSTRAP="${INSTALL_ROOT}/bootstrap.conf"
KEY="$1"
VALUE="$2"

edit_bsc() {
    sed -ie "s/\(^export $1=\).*/\1$2/" "${BOOTSTRAP}" || die "Failed to modify ${BOOTSTRAP}, is your environment OK?"
}

if grep -q "${KEY}" "${BOOTSTRAP}"; then
    o "Updating ${BOOTSTRAP}: ${KEY}=${VALUE}"
    edit_bsc "${KEY}" "${VALUE}"
else
    die "No key matching ${KEY} in ${BOOTSTRAP}"
fi
