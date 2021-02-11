#!/usr/bin/env bash
# curl -sS http://cache.local/ova/zerofill.sh | bash
process() {

### ephemera reduction
echo "Reducing ephemera"
sudo package-cleanup -y --oldkernels --count=1
sudo yum -y clean all
sudo find /home -type f -name 'registry.crt' -exec rm -f {} \;

echo "Truncating /var/logs"
sudo find /var/log -type f -exec truncate --size 0 {} \;

echo "Removing other logs"
rm $HOME/ECS-CommunityEdition/install.log

echo "Removing histories"
sudo find /home -name '.bash_history' -exec rm -f {} \;
sudo find /root -name '.bash_history' -exec rm -f {} \;
sudo history -c
history -c

rm -f $HOME/admin/bin/*.sh

### filesys reduction
echo "Defragmenting XFS /"
sudo xfs_fsr -vvvv /
sync; sync

echo "Zero-filling /"
count=$(df --sync -kP / | tail -n1  | awk -F ' ' '{print $4}')
count=$(($count-1))
sudo dd if=/dev/zero of=/tmp/zerofill.tmp bs=1M count=${count} & pid=$!
sleep 2
while sudo kill -USR1 ${pid}; do sleep 1; done
sudo rm -f /tmp/zerofill.tmp

echo "Zero-filling /boot"
count=$(df --sync -kP /boot | tail -n1  | awk -F ' ' '{print $4}')
count=$(($count-1))
sudo dd if=/dev/zero of=/boot/zerofill.tmp bs=1M count=${count} & pid=$!
sleep 2
while sudo kill -USR1 ${pid}; do sleep 1; done
sudo rm -f /boot/zerofill.tmp

echo "Zero-filling swap"
swapuuid="$(/sbin/blkid -o value -l -s UUID -t TYPE=swap)";
if ! [ -z "${swapuuid}" ]; then
    swappart="$(readlink -f /dev/disk/by-uuid/${swapuuid})";
    /sbin/swapoff "${swappart}";
    dd if=/dev/zero of="${swappart}" bs=1M || echo "dd exit code $? is suppressed";
    /sbin/mkswap -U "${swapuuid}" "${swappart}";
fi

### shutdown
echo "Powering off"
sudo shutdown -h now

}

process
