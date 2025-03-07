#!/bin/bash
# Copyright (c) 2013 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.
#

date

# TODO import this only for k8s deployment
test -e kubernetes_lib.sh && source kubernetes_lib.sh

# This script will generate the partition file (ss-partition-conf.json) to be used on this server if one is not found.
# Also a general configuration file will be generated with main parameters and a ss uuid.
# Assumes this is running on gen 3 hardware or a vipr data test node using disks mounted with a
# /dae/uuid-58f917ab-23ba-457f-a9df-d0f4b0597e2d type pattern or will look for /data (vipr)

export configdir="/opt/storageos/conf"

export p_configfile="$configdir/storageserver-partition-conf.json"
export configfile="$configdir/storageserver.conf"
export agent_config="/host/data/agent.json"

blockbinsizegb=${STORAGESERVER_PARTITION_CONFIG__BLOCKBINSIZEGB:-10}
vm_part_count=${STORAGESERVER_PARTITION_CONFIG__VM_PART_COUNT:-5}
vm_bb_cout=${STORAGESERVER_PARTITION_CONFIG__VM_BB_COUNT:-5}

# if true storageserver will create blockbin files as it does on VMs
# even if runs on hardware. Added for testinf purposes.
ss_test_on_hardware=${STORAGESERVER_PARTITION_CONFIG__TEST_ON_HARDWARE:-false}

# if true, storage server will allocate all free space for block bins
# this option overrides STORAGESERVER_PARTITION_CONFIG__VM_PART_COUNT and STORAGESERVER_PARTITION_CONFIG__VM_BB_COUNT
allocate_space_for_blockbins=${STORAGESERVER_PARTITION_CONFIG__ALLOCATE_SPACE_FOR_BLOCKBINS:-false}

# if true, storage server needs privileged container and will verify partition UUIDs
enable_partition_uuid_verifying=${STORAGESERVER_PARTITION_CONFIG__ENABLE_PARTITION_UUID_VERIFYING:-true}

function setopt() {
    opt=$1
    val=$2
    if grep -q "$opt" "$configfile" ; then
        sed -i "s#$opt=.*#$opt=$val#g" "$configfile"
    else
        echo "$opt=$val" >> $configfile
    fi
}

echo "creating main config file: $configfile"
if [ ! -e "$configfile" ]; then
    echo "creating $configfile"
    mkdir -p "$configdir"
    cat << EOF > "$configfile"
listenaddress=0.0.0.0
port=9099
blockbinsizegb=${blockbinsizegb}
logtoconsole=false
logtosyslog=true
maxoutstandingrequests=0
initblockbins=0
netserverListenPort=9069
netserverLogLevel=INFO
ioThreadNumber=400
perfCountEnabled=true
bufferPoolMaxMemThreshold=90
bufferPoolReleaseMemThreshold=50
sendQHighWaterMark=1000
recvThreadNicePriority=-15
sendThreadNicePriority=-15
enableAffinity=true
partitionroot=/dae
cacheRoot=/cache
cacheJournalRoot=/data/ss-cache-journal
trustStore=/host/data/security/truststore.pem
verifyCerts=true
cacheCleanerThreshold=90
dumperSleepDurationInSec=10
useSendfileSyscall=false
verifyPartUuid=${enable_partition_uuid_verifying}
verifyPartUuidUtility=/opt/storageos/bin/volumechk
engine=cheetah
EOF
else
    echo "$configfile already exists, no action taken"
fi

if [ "${DEPLOY_ENV}" != "kubernetes" ];
then
    setopt maxMemThresholdKb 4194304
else
    setopt engine cheetah
fi

if grep -q -E 'VMware.*Virtual.*disk' /proc/scsi/sg/device_strs && ! test -e "$agent_config" || $ss_test_on_hardware || ${allocate_space_for_blockbins} && [ ! -e /data/is_community_edition ]
then
    # this a virtual datanode, creating a json file with predefined values
    if ${allocate_space_for_blockbins}; then
        echo "Using json config file - allocating space for block bins"
    else
        echo "Using json config file - assuming hardware as virtual node for testing purpose"
    fi

    setopt partitionconfig $p_configfile
    setopt partitionroot=/dae
    root="/data/storageserver"
    mkdir -m 777 -p $root

    if ${allocate_space_for_blockbins}
    then
        volume_prefix="${root}/uuid-"
        volume_prefix_length=${#volume_prefix}

        for volume in $(find ${volume_prefix}* -maxdepth 0 -type d 2>/dev/null)
        do
            # Make sure volume supports fallocate
            bb_alloc_mode="truncate"
            if fallocate -l1k ${volume}/test-fallocate; then
                echo "fallocate is supported on ${volume}"
                bb_alloc_mode="fallocate"
            fi
            rm ${volume}/test-fallocate

            files_counter=$(ls -c1 ${volume} 2>/dev/null | wc -l)

            if [ ${files_counter} -eq 0 ]
            then
                # if we run under kubernetes we can calculate blockbin count
                if [ "${DEPLOY_ENV}" == "kubernetes" ]; then
                    # we need to invoke this here to save maps context declared in kubernetes_lib
                    fillVolumeCashMaps $volume
                    blockbin_count=$(getBlockbinCount $volume $blockbinsizegb)
                    create-block-bins.sh --path ${volume} --size "${blockbinsizegb}G" --count "${blockbin_count}" --mode ${bb_alloc_mode}
                else
                    if [ "x${STORAGESERVER_PARTITION_CONFIG__FORCE_BLOCKBIN_COUNT}" == "x" ]
                    then
                        create-block-bins.sh --path ${volume} --size "${blockbinsizegb}G" --mode ${bb_alloc_mode}
                    else
                        create-block-bins.sh --path ${volume} --size "${blockbinsizegb}G" --count "${STORAGESERVER_PARTITION_CONFIG__FORCE_BLOCKBIN_COUNT}" --mode ${bb_alloc_mode}
                    fi
                fi
            fi
        done

        if [ ! -e "$p_configfile" ]; then
            echo "creating $p_configfile"
            mkdir -p "$configdir"

            printf '{\n%2s"disks": [\n' > $p_configfile
            is_first_disk=true
            for volume in $(find ${volume_prefix}* -maxdepth 0 -type d 2>/dev/null)
            do
                if ! ${is_first_disk}
                then
                    echo "," >> $p_configfile || echo "" >> $p_configfile
                fi

                # if we run under kubernetes need to obtain volume uuid
                if [ "${DEPLOY_ENV}" == "kubernetes" ]; then
                    # if we can't find id in cash we need to update it
                    if [ -z "$(getVolumeId $volume)" ]; then
                        fillVolumeCashMaps $volume
                    fi
                    uuid=$(getVolumeId $volume)
                else
                    uuid=${volume:${volume_prefix_length}}
                fi
                printf '%4s{\n%6s"uuid": "'$uuid'",\n%6s"mount_path": "'$volume'",\n%6s"health": "Good"\n%4s}' >> $p_configfile

                is_first_disk=false
            done
            printf '%2s]\n}' >> $p_configfile
        else
            echo "$p_configfile already exists, no action taken"
        fi
    else
        bb_alloc_cmd="truncate --size ${blockbinsizegb}G "
        if fallocate -l1k $root/test-fallocate; then
            echo fallocate is supported
            bb_alloc_cmd="fallocate -l${blockbinsizegb}G "
        fi
        rm $root/test-fallocate

        for part in $(seq 1 $vm_part_count); do
            for bb in $(seq 1 $vm_bb_cout); do
                bb=$(printf "%0*d\n" 4 $bb)
                mkdir -m 777 -p $root/uuid-$part
                $bb_alloc_cmd$root/uuid-$part/$bb
                chmod 777 $root/uuid-$part/$bb
            done
        done

        if [ ! -e "$p_configfile" ]; then
            echo "creating $p_configfile"
            mkdir -p "$configdir"

            printf '{\n%2s"disks": [\n' > $p_configfile
            for part in $(seq 1 "$vm_part_count"); do
                printf '%4s{\n%6s"uuid": "'$part'",\n%6s"health": "Good"\n%4s}' >> $p_configfile
                [ "$part" -lt "$vm_part_count" ] && echo "," >> $p_configfile || echo "" >> $p_configfile
            done
            printf '%2s]\n}' >> $p_configfile

        else
            echo "$p_configfile already exists, no action taken"
        fi
    fi

else
    # this is a commodity hardware node. do not generate a json file - ss will use dbus to obtain partitions
    echo "commodity node detected - using dbus api"
fi

if ! grep --quiet "uuid" "$configfile"; then
    echo "getting node id"

    node_id=$(cat /host/data/id.json 2>/dev/null | python -c 'import json,sys; print (json.load(sys.stdin)["agent_id"])' 2>/dev/null)

    if [ -z "${node_id}" ]
    then
        echo "unable to get node id"
        exit 1
    else
        setopt uuid "${node_id}"
    fi
fi

exit 0
