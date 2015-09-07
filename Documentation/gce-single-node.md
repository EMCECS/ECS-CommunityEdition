# ECS SW 2.0 Google Compute Engine Deployment

ECS 2.0 Single Node installation on Google Compute Engine: 

The following set of commands will allow you to install ECS 2.0 software on a GCE environment, with a couple of commands

## Google Compute Engine Tool Requirements
Install gcloud tools
- **[gcloud Tools Install](https://cloud.google.com/sdk/gcloud/ "gcloud Tool Guide")**


## Requirements 
The following are the base requirements for running ECS 2.0 software for a single node install, this will be created as part of the gcloud commands below:


- **Operative system:** CentOS 7.1
- **CPU/Cores:** 4 Cores
- **Memory:** Minimum of 50 GB RAM (64 GB recommended)
- **Disks:** An un-partitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts.


## Creating a new RAW disk
This will create a new disk with the name "disk1" that will be used for ECS data storage.
gcloud compute disks create disk1 --size 250 --zone us-central1-f

## Create Firewall rules
This will open up ports required by ECS, note this will be created as part of your default network.

gcloud compute firewall-rules create ecs --allow tcp:9020,tcp:9024,tcp:4443,tcp:9011,tcp:22,tcp:80,tcp:443

## Start and Run Single Node ECS
This is a single command that will do the following

1. Create a new instance of type n1-highmem-8 with 50 GB Ram
2. Attach previously created data disk "disk1"
3. reference  gce-startup.sh script, this can be found under the git repository ./ECS-CommunityEdition/ecs-single-node/gce/gce-startup.sh

gcloud compute instances create ecs1 --image=centos-7 --disk name=disk1,mode=rw,auto-delete=yes --machine-type n1-highmem-8 --preemptible --metadata-from-file startup-script=./ECS-CommunityEdition/ecs-single-node/gce/gce-startup.sh --zone us-central1-f

## Cleanup
cleaning up instance, disk and networks created (note the disk will be automatically deleted once the instance is deleted)

gcloud compute instances delete ecs1

gcloud compute firewall-rules delete ecs



