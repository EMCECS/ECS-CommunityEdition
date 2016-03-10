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

# This script will generate the partition file (ss-partition-conf.json) to be used on this server if one is not found.
# Also a general configuration file will be generated with main parameters and a ss uuid.
# Assumes this is running on gen 3 hardware or a vipr data test node using disks mounted with a
# /dae/uuid-58f917ab-23ba-457f-a9df-d0f4b0597e2d type pattern or will look for /data (vipr)

export configdir="/opt/storageos/conf"

export p_configfile="$configdir/storageserver-partition-conf.json"
export configfile="$configdir/storageserver.conf"

blockbinsizegb=10
vm_bb_cout=5
vm_part_count=5

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
iothreads=100
blockbinsizegb=$blockbinsizegb
debugenabled=false
logtoconsole=false
logtosyslog=true
maxoutstandingrequests=0
initblockbins=0
netserverListenPort=9069
netserverLogLevel=INFO
ioThreadNumber=200
perfCountEnabled=true
maxMemThresholdKb=3145728
sendQHighWaterMark=1000
partitionroot=/dae
agentUrlEndPoint=/host/data/agent.json
agentDisksRestFragment=/v1/agent/node/storage/disk/disks
trustStore=/host/data/security/truststore.pem
verifyCerts=true
dbusEnabled=false
EOF
else
    echo "$configfile already exists, no action taken"
fi

if grep -q -E 'VMware.*Virtual.*disk' /proc/scsi/sg/device_strs && [ ! -e /data/is_community_edition ]
then
    # this a virtual datanode, creating a json file with predefined values
    echo "virtual node detected - using json config file"
    setopt partitionconfig $p_configfile
    setopt partitionroot=/dae
    root="/data/storageserver"

    for part in $(seq 1 $vm_part_count); do
        for bb in $(seq 1 $vm_bb_cout); do
            bb=$(printf "%0*d\n" 4 $bb)
            mkdir -m 777 -p $root/uuid-$part
	        fallocate -l${blockbinsizegb}G $root/uuid-$part/$bb
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
else
    # this is a commodity hardware node. do not generate a json file - ss will use dbus to obtain partitions
    echo "commodity node detected - using dbus api"
fi

if ! grep --quiet "uuid" "$configfile"; then
    echo "generating server uuid"
    uuidgen="$(which uuidgen)"
    if [ ! -z "$uuidgen" ]; then
        uuid="$(uuidgen)"
    else
        echo "warning: uuidgen utility was not found on your system. using timestamp as a uuid"
        uuid="$(date +%s)"
    fi
    setopt uuid "$uuid"
fi
