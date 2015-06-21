# ECS Software 2.0 - Multi-Node Docker Configuration Instructions


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
- [Files Inventory](#files-inventory)
- [Support](#support)



## Introduction

EMC's Elastic Cloud Storage (ECS) 2.0 Software Docker **Multiple node** deployment is intended to be used by developers and has a range of deployment options for them. The most universal methods for deploying ECS software is through Docker applied across whichever means at your disposal (IaaS/PaaS/Hypervisor). In addition to this, you can leverage Vagrant for local VirtualBox instances.

In terms of cloud deployments, there are a range of options here. The most compatible methods of deployment across any provider is the CentOS and CoreOS options to run the Docker instances. 



## Global Requirements

An ECS cluster deployment requires a minimum of four (4) data nodes to provide the feature set required. Each one of the instances should have the following minimum requirements: 

- **Operative system:** CentOS 7
- **CPU/Cores:** 4 Cores
- **Memory:** Mininum of 30 GB RAM
- **Disks:** An unpartitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts.


### Supported Host Operative Systems

We have performed testing against the following platforms: 

OS Name | Version | Docker Version |
|-------|---------|----------------|
|CentOS	| 7.1	  | 1.4.1          |

## Versioning

ECS 2.0 Software on Docker consists of images for different platforms, install scripts, and documentation. Individual portions for different platforms will be updated independently. Please use this Github repository and versioning table at the bottom of this page as the location to check for the latest releases.

## Installation Steps

The installation script is composed by two main steps:

|Step| Name | Description |Execution Time |
|------|------|-----------|---------------|
|1| Host Configuration | Step 1 of the single node installation. This step controls the flow and contains the configuration changes required for the Host OS that will run the ECS 2.0 Software Docker container.|1-5 min|
|2|ECS Object Configuration  |  Step 3 of the single node installation using Python. This step performs the ECS configuration so it can start serving objects.|5-15 min|


## CentOS Installation

[CentOS](http://www.centos.org/) is a well known Linux distribution that has the ability to deploy containers with Docker. Common public cloud platforms have CentOS templates ready to be used, so getting ECS 2.0 Software on a Docker container up is extremely easy!


### Pre Installation Steps

These steps are to be performed prior running the installation scripts on each of the ECS Nodes:

1. **Attach Data Disk(s):** ECS requires one or more disks to be attached to the host. The disk(s) will hold the object data store. The minimum is one data disk per data node. More disks can be added to increase total storage and performance. For testing purposes you can attach a disk above 512 GB. **The Disks will be formatted as XFS by the installation script**

	The Data Disk(s) attached to each host need to be **unpartioned or RAW**. For example: We have a new host where we execute an `fdisk -l`:
	
	![Fdisk in a new Host ](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step1.PNG)

	In the picture we can see two disks sda and sdb. A `mount -l` looks like this: 

	![Mount in a new Host](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step2.PNG)

	Now, we attach a new disk to the Host VM. The new disk **/dev/sdc** looks like this after executing `fdisk -l` again:

	![Fdisk in New Host with a new disk attached](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step3.PNG)

	**Note:** Depending on the environment or the cloud provider you maybe using, the attached Disk(s) Name will be different. On this example the attached disk came as **/dev/sdc**.

	Once you execute the STEP 1 script,  the attached disk (**/dev/sdc** in our example) will be formated and mounted:

 	![Fdisk after the STEP 1 script has executed](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step4.PNG)
	

2. **Open Ports:** ECS requires the following ports open:

	|Port Number|Port Description|
	|-----------|----------------|
	|22| SSH, needed if using remote access |
	|443 | Port used for accessing the ECS management Website|
	|9020| Port used for the S3 API|
	|9024| Port used for SWIFT API |
	|4443| ECS Management API Port *|
	|9011| ECS Management API Port *|

	**Note:** Ports 4443 and 9011 should be open on the ECS Data nodes if you choose to run Step 2 via the provided script vs. using the ECS management website.

	You may need more ports open, please refer to the **[ECS Security Configuration Guide](https://community.emc.com/docs/DOC-45012)** if you find any issues.


3. **Network configuration:** Define your network configuration. ECS Data nodes should be on the same Subnet and they should be able to talk to each other. This is an example:

	![ECS Multinode network configuration example](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecc-host-network-example.png)
	

### Host Configuration


1. **Get the Scripts:** Clone or copy this GitHub repository into the Host OS.

2. **Gather** the IP Addresses, Hostnames and disc(s) to be used on each one of the hosts. For Example:
	
	|Hostname | IP Address | Disk Name|  
 	|---------|------------|----------|
	|ecstestnode1 | 10.0.1.10 |sdc sdd |
	|ecstestnode2 | 10.0.1.11 |sdc sdd |
	|ecstestnode3 | 10.0.1.12 |sdc sdd |
	|ecstestnode4 | 10.0.1.13 |sdc sdd |


### Host and Container Configuration

The following section needs to be performed on each one of the ECS Nodes:

1. Copy the  **/ecs-multi-node** folder on each one of the ECS Nodes. You can use the following **SCP** command:

	`scp -P 63090 -r ecs-multi-node User_name_on_ECS_Node@IP_Address_Of_ECS_Node:/home/User_name_on_ECS_Node`

2. Use gathered values of each ECS node (IP addresses, Hostnames, Disk Names) to build the  `step1_ecs_multinode_install.py` script:

	|Variable Name|Variable Description | Example Value|
	|-------------|---------------------|--------------|
	| ips | IP Address of the ECS Nodes |10.0.1.10 10.0.1.11 10.0.1.12 10.0.1.13 |
	| hostnames | Hostnames of the ECS Nodes | ecstestnode1 ecstestnode2 ecstestnode3 ecstestnode4 |
	| disks |Name of the disks to be attached for each ECS Node. You can attach one or more disks on each data node | sda sdc sdd |

	The command should look like this: 
	
	    sudo python step1_ecs_multinode_install.py --ips 10.0.1.10 10.0.1.11 10.0.1.12 10.0.1.13 --hostnames ecstestnode1 ecstestnode2 ecstestnode3 ecstestnode4 --disks sdc sdd
	
	**The execution of this script is will take about 1-5 minutes** depending of how many packages need to be updated. This script executed should be executed on each ECS Node.

3. Once this step has finished, **you may have to wait a few minutes** until the administrator website is available from one of the ECS data nodes. The ECS Administrative portal can be accessed from any one of the ECS data nodes on port 443. For example: https://ecs-node-ip-address. Once you see the screen bellow, you are now ready to execute STEP 2.    

![ECS UI](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-waiting-for-webserver.PNG)


### ECS Object Configuration 

The next step, is the ECS Object configuration. This can be accomplished in two ways: 

- **ECS' Administration UI:** [Please follow these Instructions.](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Web-Interface.md "ECS UI Object Configuration via Administration website")

	or

- **Automated script:** Follow the instructions in the section below.

Both methods provide the same results, one of them walks you through the ECS's administrative web interface and the second uses the ECS's Management API (exposed on port 4443)


**ECS Object Configuration via an automated script**


1. Navigate to the  **/ecs-multi-node** folder 
2. Copy the `step2_object_provisioning.py` script to the host or machine that can access the 4443 port on any of the ECS Nodes.
2. Before executing the `step2_object_provisioning.py` please, please provide values for the following variables:
	
	|Variable Name|Variable Description | Example Value|
	|-------------|---------------------|--------------|
	|ECSNodes | IP Addressess of the ECS Nodes (coma delimited list). | 10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13 |
	|NameSpace | The objects' Namespace | ns1 |
 	|ObjectVArray | The objects' Virtual Array | ova1 |
	|ObjectVPool | The objects' Virtual Pool | ov1 |
	|DataStoreName | The name of the Data Store.| ds1 |
	|VDCName | The name of the Virtual Data Center.| vdc1 |
	|MethodName | The name of step to be executed. Leave blank for automated and add a value for a manual installation| [empty] |
	
	Once the variables are defined, they should be placed in the script. The command looks like this: 

	**step2_object_provisioning.py** --ECSNodes=`Coma seperated list of datanodes` --Namespace=`namespace` --ObjectVArray=`Object vArray Name` --ObjectVPool=`Object VPool name` --UserName=`user name to be created` --DataStoreName=`Name of the datastore to be created` --VDCName=`Name of the VDC` --MethodName=`Operation to be performed`
	
	Using the example values, the command would look like this: 
	
		sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=
	
	For more granular way of executing the Object Configuration, you can follow the instructions on  **[this document](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Automation.md "ECS UI Automation Detailed")** that show how to run the process step by step. 

	**The execution of this script may take about 5 to 30 min to complete**


### ECS Web Environment access and object testing

After the successful execution of the ECS Object Configuration, the system is ready to start serving objects.

In addition, access to the ECS's admin panel is available via the HTTPS. Using our previous example for ECS deployed on 10.0.0.4. Access should be enabled for https://IP-Address-of-ECS-Node. Default login and password: `root/ChangeMe`
  




## Files Inventory

ECS Multiple Node installation files are located in the **/ecs-multi-node** folder

|File Name| Description |
|--------|-------------|
|step1_ecs_multinode_install.py | Step 1 of the single node installation. This step controls the flow and contains the configuration changes required for the Host OS that will run the ECS 2.0 Software Docker container|
|step2_object_provisioning.py| Step 2 of the single node installation using Python. This step performs the ECS configuration so it can start serving objects |
|settings.py| Settings file that holds the installation scripts logging configuration |
|license.xml| ECS License file |



## Support

Please file bugs and issues at the Github issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a> or tagged with **EMC** on <a href="https://stackoverflow.com">Stackoverflow.com</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
