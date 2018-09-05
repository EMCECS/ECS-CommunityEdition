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
echo "Defragmenting /"
sudo xfs_fsr -vvvv /
sync; sync

echo "Zero-filling /"
sudo dd if=/dev/zero of=/tmp/zerofill.tmp bs=10M & pid=$!
sleep 2
while sudo kill -USR1 $pid; do sleep 1; done
sync; sync
sudo rm -f /tmp/zerofill.tmp
sync; sync

### shutdown
echo "Powering off"
sudo shutdown -h now

}

process
