#!/usr/bin/env bash

# CentOS Get Updates
yum update -y

# Install Packages CentOS
yum install wget tar -y

#Disable SELinux
setenforce 0

# Download Docker
wget http://cbs.centos.org/kojifiles/packages/docker/1.4.1/2.el7/x86_64/docker-1.4.1-2.el7.x86_64.rpm

# Install Docker for CentOS
yum install docker-1.4.1-2.el7.x86_64.rpm -y

service docker start

#Get the additional Preparation file
wget https://emccodevmstore001.blob.core.windows.net/test/additional_prep.sh
chmod 777 additional_prep.sh

#Get the Docker Image from the EMC Corporation DockerHub repository
docker pull emccode/ecsstandalone:v2.0

# Create the network.json file
ip=$(hostname -i)
hn=$(hostname)
printf '{"private_interface_name":"eth0","public_interface_name":"eth0","hostname":"%s","public_ip":"%s"}' $hn $ip > network.json

# Seeds File needs to pre-configured
# Seeds file needs to contain all the ip addresses of the nodes that will be part of the cluster
# The seeds.example file is a coma delimited list of IPs
# Example: 10.4.0.1,10.4.0.2,10.4.0.3
#echo $ip > seeds.example

# Formating and preparation of the the Attach Disk that will hold the Object Data
echo -e "o\nn\np\n1\n\n\nw" | fdisk /dev/sdc
mkfs.xfs /dev/sdc1
mkdir -p /ecs/uuid-1
mount /dev/sdc1 /ecs/uuid-1

# Executing Addtional Preparation Script
additional_prep.sh /dev/sdc1

# Prepare Permisions for Directory and Copy files
chown -R 444 /ecs
mkdir -p /host/data
mkdir -p /host/files
cp network.json /host/data
cp seeds /host/files
chown -R 444 /host
mkdir -p /var/log/vipr/emcvipr-object
chown 444 /var/log/vipr/emcvipr-object
mkdir /data
chown 444 /data

# Fix SELinux permissions on the folders
mv /etc/sysconfig/docker /etc/sysconfig/dockerold

# Start the Docker Service and Check Status
service docker restart
service docker status

# Execute docker container
docker run -d -e SS_GENCONFIG=1 -v /ecs:/disks -v /host:/host -v /var/log/vipr/emcvipr-object:/opt/storageos/logs -v /data:/data:rw --net=host emccode/ecsstandalone:v2.0
docker ps
