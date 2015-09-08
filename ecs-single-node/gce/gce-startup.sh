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

echo "Upload License"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=UploadLicense

echo "CreateObjectVarray"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateObjectVarray

echo "CreateDataStore"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateDataStore

echo "InsertVDC"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=InsertVDC

echo "CreateObjectVpool"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateObjectVpool

echo "CreateNamespace"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateNamespace

echo "CreateUser"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateUser

echo "CreateSecretKey"
python step2_object_provisioning.py --ECSNodes=ecs1 --Namespace=ns1 --ObjectVArray=sp1 --ObjectVPool=rg1 --UserName=user1 --DataStoreName=ds1 --VDCName=vdc1 --MethodName=CreateSecretKey

echo "Done! Try it out"
