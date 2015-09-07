# ECS SW 2.0 Google Compute Engine Deployment

ECS 2.0 Single Node installation on Google Compute Engine: 

The following instructions will allow you to install ECS 2.0 software on a Google Compute Engine.

## Prerequisite -
Install Google Compute Engine Tools
- **[gcloud Tools Install](https://cloud.google.com/sdk/gcloud/ "gcloud Tool Guide")**


## Evnvironment Requirements 
The following are the base requirements for running ECS 2.0 software for a single node install, this will be created as part of the gcloud commands below:


- **Operative system:** CentOS 7.1
- **CPU/Cores:** 4 Cores
- **Memory:** Minimum of 50 GB RAM (64 GB recommended)
- **Disks:** An un-partitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts.


##1. Creating a new RAW disk
This will create a new disk with the name "disk1" that will be used for ECS data storage:

    gcloud compute disks create disk1 --size 250 --zone us-central1-f

##2. Create Firewall rules
This will open up ports required by ECS, note this will be created as part of your default network.

    gcloud compute firewall-rules create ecs --allow tcp:9020,tcp:9024,tcp:4443,tcp:9011,tcp:22,tcp:80,tcp:443

##3. Start VM Instance and Install ECS from a startup script
This gcloud command will create a new VM instance of type high memory with 8 core and 50 GB RAM. Second it will attach the previously created disk and run a startup script that will install ECS on the node. 

Note I am using here a preemtible GCE node type, this means it lasts only 24 hours. If you are looking to run this for sometime remove this option.

1. Create a new instance of type n1-highmem-8 with 50 GB Ram
2. Attach previously created data disk "disk1"
3. reference  gce-startup.sh script, this can be found under the git repository ./ECS-CommunityEdition/ecs-single-node/gce/gce-startup.sh


**gcloud compute instances create ecs1 --image=centos-7 --disk name=disk1,mode=rw,auto-delete=yes --machine-type n1-highmem-8     --preemptible --metadata-from-file startup-script=./ECS-CommunityEdition/ecs-single-node/gce/gce-startup.sh --zone      us-central1-f**

The script will attempt to login using curl, this may take from 10 - 15 minutes. Once this is completed the script will start the provisioning process which may take upto 20 minutes. If the process gets stuck you can log into the ECS UI to complete the provisioning process. - [Please follow these Instructions.](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Web-Interface.md "ECS Manual Provisioning using ECS Web UI")


##4. Monitor Node Status
In order to monitor the installation process, you need to get a serial port dump from GCE, this can be done using the following command:

    gcloud compute instances get-serial-port-output --zone us-central1-f ecs1

##5. Access the ECS Web UI

 The ECS Administrative portal can be accessed from any one of the ECS data nodes via HTTPS on port 443. For example: https://ecs-node-ip-address. Once you see the screen below:

![ECS UI](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-waiting-for-webserver.PNG)



##6. Cleanup
Now once you are done, you can cleaup instance, disk and networks created (note the disk will be automatically deleted once the instance is deleted)

    gcloud compute instances delete ecs1

    gcloud compute firewall-rules delete ecs



