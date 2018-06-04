#!/usr/bin/env bash
# curl -sS http://cache.local/ova/zerofill.sh | bash
process() {

echo "Reducing ephemera"
sudo package-cleanup -y --oldkernels --count=1
sudo yum -y clean all

echo "Truncating /var/logs"
sudo find /var/log -type f -exec truncate --size 0 {} \;

echo "Defragmenting /"
sudo xfs_fsr -vvvv /

echo "Removing other logs"
rm $HOME/ECS-CommunityEdition/install.log

echo "Removing histories"
sudo find /home -name '.bash_history' -exec rm -f {} \;
sudo find /root -name '.bash_history' -exec rm -f {} \;
sudo history -c
history -c

echo "Zero-filling /"
sudo dd if=/dev/zero of=/tmp/zerofill.tmp bs=10M & pid=$!
sleep 5
while sudo kill -USR1 $pid; do sleep 1; done
sudo rm -f /tmp/zerofill.tmp

echo "Powering off"
sudo shutdown -h now

}

process
