#@IgnoreInspection BashAddShebang

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# Plugin defaults, functions can be overridden if 'unset' first:

os_supported=false

# Caller symlinks
unset symlink_scripts
symlink_scripts() {
    symlinks="ecsdeploy catfacts enter pingnodes step1 step2 island-step1 island-step2 update_deploy update_image rebuild_image inventory testbook videploy"
    symlinks="${symlinks} island-step3 ecsconfig ecsremove"
    mkdir -p "${HOME}/bin"
    for l in $symlinks; do
        ln -s "${root}/ui/run.sh" "${HOME}/bin/$l" 2>/dev/null
    done
}
