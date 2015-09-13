# ECS SW 2.0 Google Compute Engine Deployment

ECS 2.0 Single Node installation on Google Compute Engine: 

The following instructions will allow you to install ECS 2.0 software using a GCE Deployment Manager with a single command.

## Prerequisite -
Install Google Compute Engine Tools
- **[gcloud Tools Install](https://cloud.google.com/sdk/gcloud/ "gcloud Tool Guide")**


## Evnvironment Requirements 
The following are the base requirements for running ECS 2.0 software for a single node install, this will be created as part of the gcloud commands below:


- **Operative system:** CentOS 7.1
- **CPU/Cores:** 4 Cores
- **Memory:** Minimum of 50 GB RAM (64 GB recommended)
- **Disks:** An un-partitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts.


## Deploy ECS Single Node Install

Using GCE Deployment Manager to deploy a single node ECS. Please make sure to reference the right template from ECS-CommunityEdition/ecs-single-node/gce/ecs_singlenode.yaml

Deployment Manager is GCE's deployment orchestration tool. It enables developers/ops to describe deployments using templates so it is easier to consume, manage and deploy. The following is a deployment template that basically does the following;

1. Open required firewall ports for ECS
2. Create a new data disk of 100 GB size.
2. Create a new VM Instance of type n1-highmem-8 (8core 50GB)
3. Attach Disk
4. Assign Network
5. Run a startup script for installing and provisioning ECS.

Note I am using here a preemtible GCE node type, this means it lasts only 24 hours. If you are looking to run this for sometime remove this option from the template.

```
gcloud deployment-manager deployments create ecs-deployment --config ./ecs_singlenode.yaml
```

After the installation has completed the script will attempt to login using curl, this may take from 10 - 15 minutes.


# Provisioning
The automated provisioning may get stuck, login into the portal and start the manual provisioning. The license is already uploaded so you will need to just provision the following in order:

1. Create Storage Pool
2. Create Virtual Data Center
3. Create Replication Group
4. Create Namespace
4. Create User and retrieve S3 Secret Key
5. Create Bucket

[For details follow these steps in the ECS Portal.](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Web-Interface.md "ECS Manual Provisioning using ECS Web UI")


## Monitor Node Status
In order to monitor the installation process, you need to get a serial port dump from GCE, this can be done using the following command:

    gcloud compute instances get-serial-port-output --zone us-central1-f ecs1

## Access the ECS Web UI

 The ECS Administrative portal can be accessed from any one of the ECS data nodes via HTTPS on port 443. For example: https://ecs-node-ip-address. Once you see the screen below:

![ECS UI](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-waiting-for-webserver.PNG)


## Cleanup
Now once you are done, you can cleaup instance, disk and networks created (note the disk will be automatically deleted once the instance is deleted)

    gcloud deployment-manager deployments delete ecs-deployment



