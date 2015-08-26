#!/bin/bash

MOUNT=/bin/mount
UMOUNT=/bin/umount
GREP=/usr/bin/grep
AWK=/usr/bin/awk
DF=/bin/df
FALLOCATE=/usr/bin/fallocate
XFS_DB=/usr/sbin/xfs_db
#XFS_CHECK=/usr/sbin/xfs_check
XFS_REPAIR=/sbin/xfs_repair
DD=/bin/dd

# size of chunk file
FILE_SIZE_GB=10

function usage {
    echo "usage: $0 <mounted_device>"
    exit 1
}

device=$1
mount_point=`$MOUNT | $GREP $device | $AWK '{print $3}'`

if [ -z "$device" -o -z "$mount_point" ]; then
    usage
fi

# mount file system to create files on it
$MOUNT | $GREP $device -q
if [ $? -eq 1 ]; then
    echo "mount $device"
    $MOUNT $device $mount_point
fi

num_files=`$DF -BG $mount_point | $GREP $mount_point | $AWK -v FGB=$FILE_SIZE_GB '{gsub("G", "", $4); print int($4 / FGB)}'`
declare -a inodes
for ((i=0;i<$num_files;i++)) {
    file=`printf "%04d\n" $i`
    echo "create file $file"
    $FALLOCATE -l ${FILE_SIZE_GB}G $mount_point/$file
    inodes[$i]=`ls -i $mount_point/$file | $AWK '{print $1}'`
}

# umount file system and force allocation of data blocks
$UMOUNT $device

for inode in ${inodes[@]}; do
    num_extents=`$XFS_DB -c "inode $inode" -c "print u.bmx" $device | $AWK '{if ($0 ~ "not found") {print 0} else {print NF - 3}}'`
    # inode locates on offset inode # * inode size (256 by default) on disk
    # and the first extent locates at offset 100 in the inode
    extent_offset=$((inode*256+100))
    for ((i=0;i<$num_extents;i++)) {
        echo "set extent $i of inode $inode at $extent_offset"
        # the extent status flag is the first two MSB
        # as the file size is just a few GB, the rest bits in the first byte are all zeros
        $DD if=/dev/zero of=$device bs=1 count=1 seek=$extent_offset > /dev/null 2>&1

        # each extent is 16 bytes
        extent_offset=$((extent_offset+16))
    }

    # show the extents after force allocation
    $XFS_DB -c "inode $inode" -c "print u.bmx" $device
done

$XFS_REPAIR -n $device
if [ $? -ne 0 ]; then
    echo "fs check failed"
    exit 1
fi

# mount again, the file system is now ready
$MOUNT $device $mount_point -o noatime
