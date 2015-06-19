# ECS SW 2.0 Single Node Vagrant Deployment

**Table of Contents**

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Using Vagrant](#using-vagrant)
  - [Troubleshooting](#troubleshooting)

## Introduction

EMC's Elastic Cloud Storage (ECS) 2.0 Software Docker **single node** deployment is intended to be used by developers and has a range of deployment options for them. The most universal methods for deploying ECS software is through Docker applied across whichever means at your disposal (IaaS/PaaS/Hypervisor). In addition to this, you can leverage Vagrant for local VirtualBox instances.


## Requirements

Remote machine:
- **Operating system:** CentOS 7
- **CPU/Cores:** 4 Cores
- **Memory:** Mininum of 30 GB RAM
- **Disks:** An unpartitioned/Raw disk with at least 100 GB. 
- `rsync` package

Local machine:
- [Vagrant](http://www.vagrantup.com/)
- [Vagrant ManagedServers plugin](https://github.com/tknerr/vagrant-managed-servers)
- `rsync` package


## CentOS Installation

[CentOS](http://www.centos.org/) is a well known Linux distribution that has the ability to deploy containers with Docker. Common public cloud platforms have CentOS templates ready to be used, so getting ECS 2.0 Software on a Docker container up is extremely easy!

These are the installation steps to perform a CentOS installation: 

### Pre-installation steps

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

### Remote host configuration

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


## Using Vagrant

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


