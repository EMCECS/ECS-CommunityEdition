# ECS Software 2.0 - Multi-Node Puppet Configuration Instructions


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

EMC's Elastic Cloud Storage (ECS) 2.0 Software Puppet **Multiple node** deployment is intended to be used by developers and Ops Who are familiar with Puppet Enterprise as configuration management system.


## Global Requirements

An ECS cluster deployment requires a minimum of three (3) data nodes to provide the feature set required. Each one of the instances should have the following minimum requirements: 

- **Operative system:** CentOS 7
- **CPU/Cores:** 4 Cores
- **Memory:** Mininum of 30 GB RAM
- **Disks:** An unpartitioned/Raw disk with at least 100 GB of Storage per disk per host. Multiple disks can be attached on each ECS Node to increase capacity and performance. Each disk need to be un-partitioned before running the installation scripts.


### Supported Host Operative Systems

We have performed testing against the following platforms: 

OS Name | Version | Docker Version |
|-------|---------|----------------|
|CentOS	| 7.1	  | 1.4.1          |


## Puppet ECS Module 

The installation Module is composed by two main manifest files:

|Step| Name | Description |
|------|------|-----------|
|1| ini.pp | Initial class|
|2| Configurate.pp  | Install and configure the node to run ECS Software|


## CentOS Installation

[CentOS](http://www.centos.org/) is a well known Linux distribution that has the ability to deploy containers with Docker. Common public cloud platforms have CentOS templates ready to be used.


### Pre Installation Requirement

These steps are to be performed prior install The module on the Puppet master server:

1. **Puppet Master:** The master server is installed and configured.

2. **Puppet Nodes:** Puppet node is installed and configured with the correct ports. ECS requires the following ports open:

	|Port Number|Port Description|
	|-----------|----------------|
	|22| SSH, needed if using remote access |
	|443 | Port used for accessing the ECS Web Application|
	|4443| Port used for accessing the ECS API. This port can be closed from external access after the installation|
	|9011| Port used for accessing the ECS API. This port can be closed from external access after the installation|
	|9020| Port used for the S3 API|
	|9024| Port used for SWIFT API |
	|61613| Puppet MCollective |
	|8140| Puppet |

	**Note:** There are more ports required to be open if you have a firewall running on the hosts. Please refer to **[List of Ports to be Open](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md#list-of-open-ports-required-on-each-ecs-data-node)** of the troubleshooting page.

	In addtion, please refer to the [ECS Security Configuration Guide](https://community.emc.com/docs/DOC-45012 "ECS Security Configuration Guide") and our the [troubleshooting page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md "troubleshooting page") if you find any issues.

3. The following [Puppet Get Start Guide](http://info.puppetlabs.com/pe-azure-gsg.html) is good reference to use.

### Install ECS Module 

**Puppet Master Server:**
 
1. From the command line on the Puppet master, navigate to the modules directory `cd /etc/puppetlabs/puppet/environments/production/modules`.
2. Run `mkdir -p ecs3datanodes/manifests` to create the new module directory and its manifests directory.
3. Run `cd ecs3datanodes/manifests`
3. Using wget download ecs manifest ini.pp `wget -q https://github.com/EMCECS/ECS-CommunityEdition/blob/master/ecs-multi-node/pupppet/ecs3datanodes/manifest/ini.pp -O ini.pp`
4. Then download ecs manifest configure.pp `wget -q https://github.com/EMCECS/ECS-CommunityEdition/blob/master/ecs-multi-node/pupppet/ecs3datanodes/manifest/configure.pp -O configure.pp`
5. Add custom Fact to check if ECS breadcrum file exists on the node machines.
	- Run `cd /etc/puppetlabs/puppet/environments/production/modules/ecs3datanodes`
	- Run `mkdir facts.d; cd facts.d`
	- Then download ecs fact checkecsfile.sh `wget -q https://github.com/EMCECS/ECS-CommunityEdition/blob/master/ecs-multi-node/pupppet/ecs3datanodes/facts.d/checkecsfile.sh -O checkecsfile.sh`
5. Run `puppet agent -t`


**Puppet Enterprise Web:**

1. From the console, click **Classification** in the top navigation bar.

2. In the** Node group name** field, name your group **ECS-DataNodes**.
3. Click **Add group**.

Note: Leave the Parent name and Environment values as their defaults **(default and production**, respectively).

4. From the **Classification** page, select the **ECS-DataNodes** group, and click the Rules tab.
5. In the **Fact** field, enter “name” (without the quotes).
6. From the **Operator** drop-down list, select **matches regex**.
7. In the **Value** field, enter “.x” (without the quotes).
8. Click **Add rule**.

**To add the ecs3datanodes classes to the ECS-DataNodes group:**

1. From the **Classification** page, select the **ECS-DataNodes** group.
2. Click the **Classes** tab.
3. In the **Class name** field, begin typing `ecs3datanodes`, and select it from the autocomplete list.
4. Click **Add class**.
6. Click the Commit change button.

7. From the CLI of your Puppet master, run `puppet agent -t`.


### Node Configuration

The following section needs to be performed on each one of the ECS Nodes:

1. From command line run agent, run ` puppet agent -t`.

2. After finishing check docker container run `docker ps`

**The execution of this script is will take about 1-5 minutes** depending of how many packages need to be updated. This script executed should be executed on each ECS Node.


### ECS Object Configuration 

The next step, is the ECS Object configuration. This can be accomplished in two ways: 

- **ECS' Administration UI:** [Please follow these Instructions.](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-UI-Web-Interface.md "ECS UI Object Configuration via Administration website")

	or

- **Automated script:** [Please follow these Instructions.](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-MultiNode-Instructions.md#ecs-object-configuration "ECS UI Object Configuration via Automated script")





### ECS Web Environment access and object testing

After the successful execution of the ECS Object Configuration, the system is ready to start serving objects.

In addition, access to the ECS's admin panel is available via the HTTPS. Using our previous example for ECS deployed on 10.0.0.4. Access should be enabled for https://IP-Address-of-ECS-Node. Default login and password: `root/ChangeMe`
  

## Troubleshooting
If you have any issues with the installatation you can **[review this page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md "Troubleshooting page")** for troubleshooting tips and/or go to the support section bellow.


## Support

Please file bugs and issues at the Github issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a> or tagged with **EMC** on <a href="https://stackoverflow.com">Stackoverflow.com</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
