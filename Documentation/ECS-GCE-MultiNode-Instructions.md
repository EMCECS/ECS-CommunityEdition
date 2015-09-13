# ECS SW 2.0 Google Compute Engine Deployment

ECS 2.0 Multi Node installation on Google Compute Engine: 

The following instructions will allow you to install ECS 2.0 software using a GCE Deployment Manager, using a simple template file.

## Prerequisite -
Install Google Compute Engine Tools
- **[gcloud Tools Install](https://cloud.google.com/sdk/gcloud/ "gcloud Tool Guide")**


## Evnvironment Requirements 
The following are the base requirements for running ECS 2.0 software for a mutli node install, this will be created as part of the gcloud commands below:


- **Operative system:** CentOS 7.1
- **CPU/Cores:** 4 Cores
- **Memory:** Minimum of 50 GB RAM (64 GB recommended)
- **Disks:** An un-partitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts.


## Deploy ECS Multi Node Install

Using GCE Deployment Manager to deploy a multi node ECS. Please make sure to reference the right template from ECS-CommunityEdition/ecs-multi-node/gce/ecs_multinode.yaml

Deployment Manager is GCE's deployment orchestration tool. It enables developers/ops to describe deployments using templates so it is easier to consume, manage and deploy. The following is a deployment template that basically does the following;

1. Create required firewall rules for ECS
2. Create a set of 4 data disk of 256 GB size each.
2. Create a set of 4 VM Instance of type n1-highmem-2 (2core 13GB)
3. Attach Disk for each node
4. Assign Network
5. Run a startup script for installing and provisioning ECS.

Note I am using here a preemtible GCE node type, this means it lasts only 24 hours. If you are looking to run this for sometime remove this option from the template.

```
gcloud deployment-manager deployments create ecs-deployment --config ./ecs-multi-node/gce/ecs_multinode.yaml
```

After the installation has completed wait 10 - 15 minutes, and then attempt to login into the ECS portal for any of the nodes.


# Provisioning
The automated provisioning may get stuck, login into the portal and start the manual provisioning. 

1. Upload License
2. Create Storage Pool
3. Create Virtual Data Center
4. Create Replication Group
5. Create Namespace
6. Create User and retrieve S3 Secret Key
7. Create Bucket

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



