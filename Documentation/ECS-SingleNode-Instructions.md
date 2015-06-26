# ECS SW 2.0 - Single-Node Docker Configuration Instructions

**Table of Contents**
- [Introduction](#introduction)
- [Global Requirements](#global-requirements)
- [Installation Steps](#installation-steps)
- [CentOS Installation](#centos-installation)
	- [Pre-Installation Steps](#pre-installation-steps)
	- [Host Configuration](#host-configuration)
	- [Host and Container Configuration](#host-and-container-configuration)
	- [ECS Object Configuration](#ecs-object-configuration)
	- [ECS Web Environment access and object testing](#ecs-web-environment-access-and-object-testing)
	- [Troubleshooting](#troubleshooting)
	- [Support](#support)



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



## Installation Steps

The installation script is composed by three main steps:

|Step| Name | Description |Execution Time |
|------|------|-----------|---------------|
|1| Host & ECS Container Configuration  | Step 1 of the single node installation. This step controls the flow and contains the configuration changes required for the Host OS that will run the ECS 2.0 Software Docker container. In addition, this step updates the ECS Docker container so it can run as a single node and with limited resources|1-5 min|
|2|ECS Object Configuration  |  Step 2 of the single node installation. This step performs the ECS configuration so it can start serving objects.|10-30 min|


## CentOS Installation

[CentOS](http://www.centos.org/) is a well known Linux distribution that has the ability to deploy containers with Docker. Common public cloud platforms have CentOS templates ready to be used, so getting ECS 2.0 Software on a Docker container up is extremely easy!

These are the installation steps to perform a CentOS installation: 

### Pre Installation Steps

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

	**Note:** There are more ports required to be open if you have a firewall running on the host. Please refer to [List of Ports to be Open](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md#list-of-open-ports-required-on-each-ecs-data-node) of the troubleshooting page.

	In addtion, please refer to the [ECS Security Configuration Guide](https://community.emc.com/docs/DOC-45012 "ECS Security Configuration Guide") and our the [troubleshooting page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md "troubleshooting page") if you find any issues.



### Host and Container Configuration

1. **Perform Updates:**  Perform a Yum update `sudo yum update` and Download packages `sudo yum install git tar wget`

2. **Git Clone/Pull** the repository: [https://github.com/EMCECS/ECS-CommunityEdition ](https://github.com/EMCECS/ECS-CommunityEdition "https://github.com/EMCECS/ECS-CommunityEdition")
3. **Find Ethernet Adapter**: Find the main Host's Ethernet Adapter. You can run this command `netstat -ie | grep -B1 "<public ip address>" | head -n1 | awk '{print $1}'`  Replace "public ip address" with the Hosts public Address. **Note:** you can also can use the `ifconfig` command.  

4. **Navigate** to the  **/ecs-single-node** folder.

5. **Gather** the IP Addresse, hostname and  designated data disc(s). For Example:
	
	|Hostname | IP Address | Disk Name|Main Ethernet Adapter|  
 	|---------|------------|----------|----------------|
	|ecstestnode1 | 10.0.1.10 |sdc    |eth0|

6. Execute the following command as SUDO. For our example the command would look like this: `sudo python step1_ecs_singlenode_install.py --disks sdc --ethadapter eth0`
	
	**The execution of this script is will take about 1-5 minutes** depending of how many packages need to be updated. This script executed should be executed on each ECS Node.

6. Once this step has finished, **you may have to wait a few minutes** until the administrator website is available from one of the ECS data nodes. The ECS Administrative portal can be accessed from any one of the ECS data nodes on port 443. For example: https://ecs-node-ip-address. Once you see the screen bellow, you are now ready to execute STEP 2.    

	![ECS UI](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-waiting-for-webserver.PNG)



### ECS Object Configuration 

The next step, is the ECS Object configuration. This can be accomplished in two ways: 

- **ECS' Administration UI:** [Please follow these Instructions.](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Web-Interface.md "ECS UI Object Configuration via Administration website")

	or

- **Automated script:** Follow the instructions in the section below.

Both methods provide the same results, one of them walks you through the ECS's administrative web interface and the second uses the ECS's Management API (exposed on port 4443 and 9011)


**ECS Object Configuration via an automated script**


1. **Navigate** to the  **/ecs-single-node** folder 
2. **Verify** that for the execution of  `step2_object_provisioning.py` scrip the environtment you are in, can access the 4443 and 9011 ports of the Host machine.
2. Before executing the `step2_object_provisioning.py` please, please provide values for the following variables:
	
	|Variable Name|Variable Description | Example Value|
	|-------------|---------------------|--------------|
	|ECSNodes | IP Address of the ECS Node. **For Single Node Deployment, only one IP is necessary**. | 10.0.1.10 |
	|NameSpace | The objects' Namespace | ns1 |
 	|ObjectVArray | The objects' Virtual Array | ova1 |
	|ObjectVPool | The objects' Virtual Pool | ov1 |
	|DataStoreName | The name of the Data Store.| ds1 |
	|VDCName | The name of the Virtual Data Center.| vdc1 |
	|MethodName | The name of step to be executed. Leave blank for automated and add a value for a manual installation| [empty] |
	
	Once the variables are defined, they should be placed in the script. The command looks like this: 

	**step2_object_provisioning.py** --ECSNodes=`Coma seperated list of datanodes` --Namespace=`namespace` --ObjectVArray=`Object vArray Name` --ObjectVPool=`Object VPool name` --UserName=`user name to be created` --DataStoreName=`Name of the datastore to be created` --VDCName=`Name of the VDC` --MethodName=`Operation to be performed`
	
	Using the example values, the command would look like this: 
	
		sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=
	
	For more granular way of executing the Object Configuration, you can follow the instructions on  **[this document](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Automation.md "ECS UI Automation Detailed")** that show how to run the process step by step. 

	**The execution of this script may take about 10 to 30 min to complete**


### ECS Web Environment access and object testing

After the successful execution of the ECS Object Configuration, the system is ready to do read / write. Object users can read / write using free tools like **[S3 browser](http://s3browser.com/ "S3 browser")**

In addition, access to the ECS's admin panel is available via the HTTPS. Using our previous example for ECS deployed on 10.0.0.4. Access should be enabled for https://IP-Address-of-ECS-Node. Default login and password: `root/ChangeMe`
  

## Troubleshooting
If you have any issues with the installatation you can **[review this page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md#ecs-software-20---troubleshooting-tips "Troubleshooting page")** for troubleshooting tips and/or go to the support section bellow.


## Support

Please file bugs and issues at the Github issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a> or tagged with **EMC** on <a href="https://stackoverflow.com">Stackoverflow.com</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
