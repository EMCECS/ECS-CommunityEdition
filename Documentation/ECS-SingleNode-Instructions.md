# ECS SW 2.0 - Single-Node Docker Configuration Instructions

**Table of Contents**
- [Introduction](#introduction)
- [Global Requirements](#global-requirements)
- [Versioning](#versioning)
- [Installation Steps](#installation-steps)
- [CentOS Installation](#centos-installation)
	- [Pre-Installation Steps](#pre-installation-steps)
	- [Host Configuration](#host-configuration)
	- [Host and Container Configuration](#host-and-container-configuration)
	- [ECS Object Configuration](#ecs-object-configuration)
	- [ECS Web Environment access and object testing](#ecs-web-environment-access-and-object-testing)
	- [Troubleshooting](#troubleshooting)
- [Files Inventory & Description](#files-inventory-&-description)


## Introduction

EMC's Elastic Cloud Storage (ECS) 2.0 Software Docker **single node** deployment is intended to be used by developers and has a range of deployment options for them. The most universal methods for deploying ECS software is through Docker applied across whichever means at your disposal (IaaS/PaaS/Hypervisor). In addition to this, you can leverage Vagrant for local VirtualBox instances.

In terms of cloud deployments, there are a range of options here. The most compatible methods of deployment across any provider is the CentOS and CoreOS options to run the Docker instances. 


## Global Requirements

All instances currently require to have the following minimum requirements: 

- **Operating system:** CentOS 7
- **CPU/Cores:** 4 Cores
- **Memory:** Mininum of 30 GB RAM
- **Disks:** An unpartitioned/Raw disk with at least 100 GB. 

### Supported Host Operative Systems and Docker Version

We have performed testing against the following platform(s): 

OS Name | Version | Docker Version |
|-------|---------|----------------|
|CentOS	| 7.1	  | 1.4.1          |



## Versioning

ECS 2.0 Software on Docker consists of images for different platforms, install scripts, and documentation. Individual portions for different platforms will be updated independently. Please use this Github repository and versioning table at the bottom of this page as the location to check for the latest releases.

## Installation Steps

The installation script is composed by three main steps:

|Step| Name | Description |Execution Time |
|------|------|-----------|---------------|
|1| Host Configuration | Step 1 of the single node installation. This step controls the flow and contains the configuration changes required for the Host OS that will run the ECS 2.0 Software Docker container.|1-5 min|
|2| ECS Container Configuration |Step 2 of the single node installation. This step updates the ECS Docker container so it can run as a single node and with limited resources.|10 secs|
|3|ECS Object Configuration  |  Step 3 of the single node installation using Python. This step performs the ECS configuration so it can start serving objects.|5-15 min|


## CentOS Installation

[CentOS](http://www.centos.org/) is a well known Linux distribution that has the ability to deploy containers with Docker. Common public cloud platforms have CentOS templates ready to be used, so getting ECS 2.0 Software on a Docker container up is extremely easy!

These are the installation steps to perform a CentOS installation: 

### Pre Installation Steps

1. **Attach Disk to Host:** ECS requires a disk to be attached to the host. This disk will hold the data (objects). For testing purposes you can attach a disk above 128 GB.
2. **Open Ports in Host:** ECS requires the following ports open:

	|Port Number|Port Description|
	|-----------|----------------|
	|22| SSH, needed if using remote access |
	|443 | Port used for accessing the ECS Web Application|
	|4443| Port used for accessing the ECS API. This port can be closed from external access after the installation|
	|9011| Port used for accessing the ECS API. This port can be closed from external access after the installation|
	|9020| Port used for the S3 API|
	|9024| Port used for SWIFT API |


### Host and Container Configuration

1. **Perform Updates:**  Perform a Yum update `Sudo yum update` and Download packages `sudo yum install git tar wget`
2. **Git Clone/Pull** the repository: https://github.com/emccode/solidsnakev2.git
3. Navigate to the  **/ecs-single-node** folder.
4. Execute the following command as SUDO: `sudo python step1_ecs_singlenode_install.py --disks= sdc` .This will take about 1-5 minutes depending of how many packages need to be updated. This script will install both Steps 1 and 2 described above. 


### ECS Object Configuration

1. Navigate to the  **/ecs-single-node** folder 
2. Before executing the last installation step, please review and define values for the following variables:
	
	|Variable Name|Variable Description | Example Value|
	|-------------|---------------------|--------------|
	|ECSNodes | IP Address of the ECS Node. For Single Node Deployment, only one IP is necessary. | 10.0.0.4 |
	|NameSpace | The objects' Namespace | ns1 |
 	|ObjectVArray | The objects Virtual Array | ova1 |
	|ObjectVPool | The objects' Virtual Pool | ov1 |
	|DataStoreName | The name of the Data Store.| ds1 |
	|VDCName | The name of the Virtual Data Center.| vdc1 |
	|MethodName | The name of step to be executed. Leave blank for automated and add a value for a manual installation| [empty] |
	
	The script will perform the following operations in order: 

	- **UploadLicense**
	- **CreateObjectVarray**
	- **CreateDataStore**
	- **InsertVDC**
	- **CreateObjectVpool**
	- **CreateNamespace**
	- **CreateUser:**  CreateUser method will return an exception that user already exists. Ignore the exception and proceed to create secret key for the user. Looks like the user is being created inspite of the exception.
	- **CreateSecretKey:** This is the S3 API secret Key used for authentication. It will be displayed at the end of the script execution and is also available in the ECS' administration portal. 

	The command looks like this: 

	**step3_object_provisioning.py** --ECSNodes=`Coma seperated list of datanodes` --Namespace=`namespace` --ObjectVArray=`Object vArray Name` --ObjectVPool=`Object VPool name` --UserName=`user name to be created` --DataStoreName=`Name of the datastore to be created` --VDCName=`Name of the VDC` --MethodName=`Operation to be performed`
	
	An example of this script's execution would look like this: 
	
	`sudo python step3_object_provisioning.py --ECSNodes=10.4.0.4 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=`

	**This step takes about 10 to 30 min to execute.** 

### ECS Web Environment access and object testing

After the successful execution of the ECS Object Configuration, the system is ready to start serving objects.

In addition, access to the ECS's admin panel is available via the HTTPS. Using our previous example for ECS deployed on 10.0.0.4. Access should be enabled for https://10.0.04. Default login and password: root / ChangeMe
  
	

## Files Inventory & Description

ECS Single Node installation files /ecs-single-node folder

|File Name| Description |
|--------|-------------|
|step1_ecs_singlenode_install.py | Step 1 of the single node installation. This step controls the flow and contains the configuration changes required for the Host OS that will run the ECS 2.0 Software Docker container|
|step2_update_container.py |Step 2 of the single node installation. This step updates the ECS Docker container so it can run as a single node and with limited resources.|
|step3_object_provisioning.py| Step 3 of the single node installation using Python. This step performs the ECS configuration so it can start serving objects |
|settings.py| Settings file that holds the installation scripts logging configuration |
|license.xml| ECS License file |


