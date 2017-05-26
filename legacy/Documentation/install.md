# ECS Installation - Step 1

### Introduction
EMC's Elastic Cloud Storage (ECS) Software is intended to be used by developers and has a range of deployment options for them. The most universal method for deploying ECS software is through Docker applied across whatever means are at your disposal (IaaS/PaaS/Hypervisor). In addition to this, Vagrant and Puppet may be leveraged for installation. ECS can be deployed as a single node or as multinode, which requires a minimum of 4 nodes. This document provides installation instructions for each of those options.

## Single Node
These options install ECS as a single node using either Docker or Vagrant

### Docker
#### Host and Container Configuration
**WARNING: This is a destructive operation. Existing data on selected storage devices will be overwritten. Existing Docker installations AND images will be removed.**

1. **Perform Updates:** Perform a Yum update using `sudo yum update` and download packages required for installation using `sudo yum install git tar wget`

2. **Git Clone/Pull** the repository: [https://github.com/EMCECS/ECS-CommunityEdition ](https://github.com/EMCECS/ECS-CommunityEdition "https://github.com/EMCECS/ECS-CommunityEdition")

3. **Navigate** to the  **/ecs-single-node** folder.

4. **Gather** the IP Address, desired hostname, ethernet adapter name (which can be obtained by executing `ifconfig` on the host) and designated data disk(s). For example:

<!--table-->
| Hostname     | IP Address | Disk Name|Ethernet Adapter|  
| ------------ | ---------- | -------- |--------------- |
| ecstestnode1 | 10.0.1.10  | sdc      | eth0           |
<!--endtable-->

5. **Run the step 1 script for single-node ECS.** For our example values the command would be the one below, but your environment's specifics will differ. Be advised that **the hostname can not be localhost**. The execution of this script will take about 3-15 minutes depending on how many packages need to be installed or updated and the speed of certain services on the host:
`# sudo python step1_ecs_singlenode_install.py --disks sdc --ethadapter eth0 --hostname ecssinglenode`
For a list of all arguments with their full descriptions and including more detailed options, use the `--help` flag, e.g. `python step1_ecs_singlenode_install.py --help`

### Vagrant
#### Additional requirements
Remote machine:
- `rsync` package

Local machine:
- [Vagrant](http://www.vagrantup.com/)
- [Vagrant ManagedServers plugin](https://github.com/tknerr/vagrant-managed-servers)
- `rsync` package

#### Remote host configuration

Login to the remote machine and perform a Yum update `sudo yum update` and download the required packages `sudo yum install rsync`

Edit the sudoers file to avoid the system from asking for the password when running sudo.

    sudo vi /etc/sudoers

Look for the line that contains `Defaults   requiretty` and comment it.

    #Defaults requiretty

Now run

    sudo visudo

And add the following lines at the end of the file.

    username     ALL=(ALL) NOPASSWD: ALL
    username     ALL=(ALL:ALL) NOPASSWD: ALL

Replace `username` by the user that is actually logging in via SSH.


#### Using Vagrant

We are going to use Vagrant to prepare a remote machine with SSH access. You will just need to configure the SSH credentials and Vagrant will take care of installing the ECS in the single node mode.

First, you will need to configure the connection details for Vagrant to be able to connect to the remote machine.

Open the vagrant file and edit the following lines:

    ml_config.vm.provider :managed do |managed, override|
      managed.server = "your_host.com"
      override.ssh.username = "your_username"
      override.ssh.password = "your_password"
      override.ssh.port = 22
      #override.ssh.private_key_path = "/path/to/bobs_private_key"
    end

If you want to use an SSH key just comment line about the password.

Now, let's link it to the remote host by running the following command.

`vagrant up`

To check that we can connect to it, we can run

`vagrant ssh`

If everything goes right, you will access the remote host. You can now exit from there and run 

`vagrant provision` 

It will prepare the remote host and install ECS in single node mode. You will be able to see the output while Vagrant is configuring the host. When it finishes, the system is ready to start serving objects. In addition, access to the ECS's admin panel is available via the HTTPS. Using our previous example for ECS deployed on 10.0.0.4. Access should be enabled for https://IP_OR_HOST. Default login and password: `root` / `ChangeMe`

## Multi-Node

### Docker
#### Host Configuration
**WARNING: This is a destructive operation. Existing data on selected storage devices will be overwritten. Existing Docker installations AND images will be removed.**

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

### Puppet
#### Puppet ECS Module 

The installation Module is composed by two main manifest files:

|Step| Name | Description |
|------|------|-----------|
|1| ini.pp | Initial class|
|2| Configurate.pp  | Install and configure the node to run ECS Software|

#### Pre Installation Requirement

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

	In addition, please refer to the [ECS Security Configuration Guide](https://community.emc.com/docs/DOC-45012 "ECS Security Configuration Guide") and our the [troubleshooting page](https://github.com/EMCECS/ECS-CommunityEdition/blob/master/Documentation/ECS-Troubleshooting.md "troubleshooting page") if you find any issues.

3. The following [Puppet Get Start Guide](http://info.puppetlabs.com/pe-azure-gsg.html) is good reference to use.

### Install ECS Module 

**Puppet Master Server:**
 
1. From the command line on the Puppet master, navigate to the modules directory `cd /etc/puppetlabs/puppet/environments/production/modules`.
2. Run `mkdir -p ecs3datanodes/manifests` to create the new module directory and its manifests directory.
3. Run `cd ecs3datanodes/manifests`
3. Using wget download ecs manifest ini.pp `wget -q https://github.com/EMCECS/ECS-CommunityEdition/blob/master/ecs-multi-node/pupppet/ecs3datanodes/manifest/ini.pp -O ini.pp`
4. Then download ecs manifest configure.pp `wget -q https://github.com/EMCECS/ECS-CommunityEdition/blob/master/ecs-multi-node/pupppet/ecs3datanodes/manifest/configure.pp -O configure.pp`
5. Add custom Fact to check if ECS breadcrumb file exists on the node machines.
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


#### Node Configuration

The following section needs to be performed on each one of the ECS Nodes:

1. From command line run agent, run ` puppet agent -t`.

2. After finishing check docker container run `docker ps`

**The execution of this script is will take about 1-5 minutes** depending of how many packages need to be updated. This script executed should be executed on each ECS Node.
