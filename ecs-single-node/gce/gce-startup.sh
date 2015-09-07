#!/bin/bash

# startup script for installing ECS on GCE

echo "Starting..."
echo "Install Packages..."
yum update -y

yum install wget -y
yum install tar -y
yum install git -y

echo "Installed!"

echo "Cloning git repo"
git clone https://github.com/EMCECS/ECS-CommunityEdition.git

echo "Change directory"
cd /ECS-CommunityEdition/ecs-single-node/

echo "Starting ECS Install Script"
python step1_ecs_singlenode_install.py --disks sdb --ethadapter eth0 --hostname ecs1

python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1

echo "Done! Try it out"
