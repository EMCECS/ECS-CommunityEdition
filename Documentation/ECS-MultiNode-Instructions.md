# ECS Software - Multi-Node Docker Configuration Instructions


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
- [Troubleshooting] (#troubleshooting)
- [Support](#support)



## Introduction

EMC's Elastic Cloud Storage (ECS) Software Docker **multiple node** deployment is intended to be used by developers and has multiple deployment options for them. The most universal method for deploying ECS software is through Docker applied across whichever means are at your disposal (IaaS/PaaS/Hypervisor). In addition to this, you can leverage Vagrant for local VirtualBox instances.

In terms of cloud deployments, there are a range of options. The most compatible methods of deployment across any provider are the CentOS and CoreOS options to run the Docker instances. 


## Global Requirements

An ECS cluster deployment requires a minimum of four data nodes to provide the full set of features. Each one of the instances should have the following minimum requirements: 

- **Operative system:** CentOS 7
- **CPU/Cores:** 3 Cores
- **Memory:** Minimum of 16 GB RAM
- **Disks:** An unpartitioned/raw disk with at least 100 GB of storage per disk. Multiple disks can be attached on each ECS node to increase capacity and performance. Each disk need to be unpartitioned before running the installation scripts.

Installation also requires internet connectivity to receive the requisite utility packages and Docker images.

### Supported Host Operative Systems

We have performed testing against the following platforms: 

OS Name | Version | Docker Version |
|-------|---------|----------------|
|CentOS	| 7.1	  | 1.8.2 (latest)        |


## Installation Steps

The installation script is composed by two main steps:

|Step| Name | Description |Execution Time |
|------|------|-----------|---------------|
|1| Host Configuration | This step controls the flow and contains the configuration changes required for the host OS that will run the ECS Software Docker container.|3-15 min|
|2|ECS Object Configuration  | This step performs the ECS configuration so it can start serving objects.|10-30 min|


## CentOS Installation

[CentOS](http://www.centos.org/) is a well-known Linux distribution with the ability to deploy containers with Docker. Common public cloud platforms have CentOS templates ready to be used, so getting ECS Software on a Docker container up is extremely easy.


### Pre Installation Steps

These steps are to be performed prior running the installation scripts on each of the ECS Nodes:

1. **Attach Data Disk(s):** ECS requires one or more disks to be attached to each host. The disk(s) will hold the object data store. **The Disks will be formatted as XFS by the installation script.**

The data disk(s) attached to each host need to be **unpartitioned or RAW**. For example: We have a new host where we execute the command `sudo fdisk -l`:

![Fdisk in a new Host ](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step1.PNG)

In the picture, we can see two disks: **sda** and **sdb**. A `mount -l` looks like this: 

![Mount in a new Host](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step2.PNG)

Now we attach a new disk to the host VM. The new disk **/dev/sdc** looks like this after executing `fdisk -l` again:

![Fdisk in New Host with a new disk attached](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step3.PNG)


**Note:** Depending on the environment or the cloud provider you maybe using, the attached disk name(s) will be different. In this example, the attached disk came as **/dev/sdc**. The attached disk will be formatted and mounted during step 1, so do not mount the ECS data disk before executing step 1:

![Fdisk after the STEP 1 script has executed](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-disk-install-step4.PNG)


2. **Open Ports:** ECS requires the following ports to be open:

In addition, please refer to the [ECS Security Configuration Guide](https://community.emc.com/docs/DOC-45012 "ECS Security Configuration Guide") and our the [troubleshooting page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md "troubleshooting page") if you find any issues.

|Port Number|Port Description|
|-----------|----------------|
|22| SSH, needed if using remote access |
|443 | Port used for accessing the ECS management website|
|3218| Port used by the CAS service|
|4443| ECS management API port |
|9020| Port used for the S3 API|
|9021| Port used for the S3 API on HTTPS|
|9022| Port used for Atmos API|
|9023| Port used for Atmos API on HTTPS|
|9024| Port used for SWIFT API|
|9025| Port used for SWIFT API on HTTPS|
|9100| Port used for DT Query service|
|9101| ECS Diagnostic Service Index |

**Note:** There are the most commonly-used ports by ECS; please refer to [List of Ports to be Open](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md#list-of-open-ports-required-on-each-ecs-data-node) of the troubleshooting page. In addition, please refer to the [ECS Security Configuration Guide](https://community.emc.com/docs/DOC-45012 "ECS Security Configuration Guide") and our the [troubleshooting page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md "troubleshooting page") if you find any issues.


3. **Network configuration:** Define your network configuration. ECS Data Nodes must be on the same subnet and be able to talk to each other. This is an example:

![ECS Multinode network configuration example](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecc-host-network-example.png)


### Host Configuration
#### :bangbang: WARNING: This is a destructive operation. Existing data on selected storage devices will be overwritten. Existing Docker installations AND images will be removed. 

**The following section needs to be performed on each one of the ECS nodes:**

1. **Perform Updates:** Perform a Yum update using `sudo yum update` and download packages required for installation using `sudo yum install git tar wget`

2. **Git Clone/Pull** the repository: [https://github.com/EMCECS/ECS-CommunityEdition ](https://github.com/EMCECS/ECS-CommunityEdition "https://github.com/EMCECS/ECS-CommunityEdition")

3. **Navigate** to the **/ecs-multi-node** folder.

4. **Gather** the IP addresses, desired hostnames, ethernet adapter name (which can be obtained by executing `ifconfig` on the host), and designated data disk(s). For example:

|Hostname | IP Address | Disk Name| Ethernet Adapter |
|---------|------------|----------|------------------|
|ecstestnode1 | 10.0.1.10 |sdc sdd | eth0 |
|ecstestnode2 | 10.0.1.11 |sdc sdd | eth0 |
|ecstestnode3 | 10.0.1.12 |sdc sdd | eth0 |
|ecstestnode4 | 10.0.1.13 |sdc sdd | eth0 |

5. Use gathered values for each ECS node (IP addresses, hostnames, ethernet adapter name, disk names) to build the `step1_ecs_multinode_install.py` script, which will be the same across all nodes. Be advised that **the hostname can not be localhost for any node**. For our example values, the command should look like this:

`sudo python step1_ecs_multinode_install.py --ips 10.0.1.10 10.0.1.11 10.0.1.12 10.0.1.13 --hostnames ecstestnode1 ecstestnode2 ecstestnode3 ecstestnode4 --disks sdc sdd --ethadapter eth0`

**The execution of this script is will take about 3-15 minutes** depending on how many packages need to be installed or updated and the speed of certain services on the host.
For a list of all arguments with their full descriptions and including more detailed options, use the `--help` flag, e.g. `python step1_ecs_singlenode_install.py --help`

6. Once this step has finished, **you may have to wait a few minutes** until the administrative web UI becomes available. ECS' administrative portal can be accessed from the data node on port 443 ( https://<ecs-node-ip-address> ). Once you see the screen bellow, you are ready to execute step 2.    

![ECS UI](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/media/ecs-waiting-for-webserver.PNG)


### ECS Object Configuration 

The next step, is the ECS Object configuration. This can be accomplished in two ways: 

- **ECS' Administration UI:** [Please follow these Instructions.](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Web-Interface.md "ECS UI Object Configuration via Administration website")
- **Automated script:** Follow the instructions in the section below.

Both methods provide the same results; the first walks you through ECS's administrative web interface and the second uses ECS's Management API (exposed on port 4443 and 9011)


**ECS Object Configuration via an automated script**


1. Navigate to the  **/ecs-multi-node** folder 
2. **Verify** that the `step2_object_provisioning.py` script for the environment that you are in can access the 4443 and 9011 ports of the host machine, such as through the output of `nmap -sT -O localhost`
3. Before executing the `step2_object_provisioning.py` please, please provide values for the following variables:

|Variable Name|Variable Description | Example Value|
|-------------|---------------------|--------------|
|ECSNodes | IP Addresses of the ECS Nodes (comma-delimited list). | 10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13 |
|NameSpace | The objects' Namespace | ns1 |
|ObjectVArray | The objects' Virtual Array | ova1 |
|ObjectVPool | The objects' Virtual Pool | ov1 |
|UserName | The name of the initial Object User | user1 |
|DataStoreName | The name of the Data Store.| ds1 |
|VDCName | The name of the Virtual Data Center.| vdc1 |
|MethodName | The name of step to be executed. Leave blank to complete all provisioning steps.| *[empty]* |

Once the variables are defined, they should be placed in the script. Using the example values, the command becomes: 

	sudo python step2_object_provisioning.py --ECSNodes=10.0.1.10,10.0.1.11,10.0.1.12,10.0.1.13 --Namespace=ns1 --ObjectVArray=ova1 --ObjectVPool=ovp1 --UserName=emccode --DataStoreName=ds1 --VDCName=vdc1 --MethodName=

For more granular way of executing the Object Configuration, you can follow the instructions on  **[this document](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Automation.md "ECS UI Automation Detailed")** showing how to run the process step by step. 

**The execution of this script may take 10 to 30 minutes to complete.**


### ECS Web Environment Access and Object Testing

After the successful execution of the ECS Object Configuration, the system is ready to begin serving objects. Object users can read and write using free tools like **[S3 browser](http://s3browser.com/ "S3 browser")**

In addition, access to the ECS's administrative panel is available via the `https://<ecs-node-ip-address>` on any node. The default login and password for the portal is `root/ChangeMe` (which you will be prompted to change when first accessing the portal)

## Troubleshooting
If you have any issues with the installation you can **[review this page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md "Troubleshooting page")** for troubleshooting tips and/or go to the support section bellow.


## Support

Please file bugs and issues at the GitHub issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a> or tagged with **EMC** on <a href="https://stackoverflow.com">Stack Overflow</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community-driven process.
