# ECS Community Edition Installation

ECS Community Edition now features a brand new installer. This installer aims to greatly improve user experience through automation. This document will guide the user through the new installation process.

## Prerequisites

Listed below are all necessary components for a successful ECS Community Edition installation. If they are not met the installation will likely fail.

### Hardware Requirements

The installation process is designed to be done from a dedicated installation node. This node will bootstrap the ECS instance and, when the process is complete, can be destroyed. Both single node and multi-node require only a single installation node. The technical requirements for this machine are minimal, but will affect the speed of the installation process. We recommend the following:

* 2 Cores
* 4 GB Memory
* 10 GB HDD
* CentOS 7 Minimal

The minimum technical requirements for the target node is as follows:
 
* 4 Cores
* 16 GB Memory
* 16 GB Minimum System Drive
* 100 GB block storage unit (raw, unpartitioned) *NOTE: this drive must be in addition to the standard OS drive*
* CentOS 7 Minimal

For multi-node installations each data node must fulfill these minimum qualifications. The installer will do a pre-flight check to ensure that the minimum qualifications are met. If they are not the installation will not continue. 

### Environmental Requirements

The following environment is required to ensure a successful installation. 

* **Network:** Currently, all nodes, installation and target, must exist on the same subnet.
* **SSH:** Installation is coordinated via SSH, however, key authentication is not yet supported and password authentication must be enabled.
* **OS:** Centos7 Minimal

### Additional Information

A single node *can* successfully run the installation procedure on itself. To do this simply input the node's own IP address as the installation node as well as the data node in the deploy.yml file.

## Getting Started

Before the data nodes can be created we have to prepare the installation node. If downloading the repository from github run `sudo yum install git -y` to install git and then `git clone [insert repo address here]`. If the repository is being added to the machine via usb drive, scp, etc. run:

* for .zip archive `unzip ECS-CommunityEdition.zip`
* for .tar.gz archive `tar -xzvf ECS-CommunityEdition.tar.gz`

## The YML File

Installation requires the creation of a YML configuration file called deploy.yml. This file *must* be written before moving on. Create this file in the `ECS-CommunityEdition` directory that was created when the repository was cloned. A template guide for writing this file can be found [here](deploy.yml.rst). 

To quickly create a template, simply: 

* run `sudo cp ~/ECS-CommunityEdition/docs/design/reference.deploy.yml /opt/emc/ecs-install/` 
* rename the file with `sudo mv /opt/emc/ecs-install/reference.deploy.yml /opt/emc/ecs-install/deploy.yml`
* then edit the file with `sudo vim /opt/emc/ecs-install/deploy.yml` *be sure to use* `sudo` *or the file will be opened as readonly and any changes made will not be written*

*note: If you find that you've edited the file without sudo privileges, the command* `:w !sudo tee %` *can be used to write the while in vim*

### bootstrap.sh

The bootstrap script configures the installation node for ECS deployment. This script can take the following arguments:
```
[Usage]
 -h              This help text

[General Options]
 -y / -n         Assume YES or NO to any questions (may be dangerous).

 -v / -q         Be verbose (also show all logs) / Be quiet (only show necessary output)

 -c <deploy.yml> If you have a deploy.yml ready to go, use this.

 -o <ns1[,ns2,]> Override DHCP-configured nameserver(s); use these instead. No spaces!

 -g              Install virtual machine guest agents and utilities for QEMU and VMWare.
                 VirtualBox is not supported at this time.

 -b <mirror>     Build the installer image (ecs-install) locally instead of fetching
                 the current release build from DockerHub (not recommended). Use the
                 Alpine Linux mirror <mirror> when building the image.

[Docker Options]
 -r <registry>   Use the Docker registry at <registry> instead of DockerHub.
                 The connect string is specified as '<host>:<port>[/<username>]'
                 You may be prompted for your credentials if authentication is required.
                 You may need to use -d (below) to add the registry's cert to Docker.

 -d <x509.crt>   NOTE: This does nothing unless -r is also given.
                 If an alternate Docker registry was specified with -r and uses a cert
                 that cannot be resolved from the anchors in the local system's trust
                 store, then use -d to specify the x509 cert file for your registry.

[Proxies & Middlemen]
 -k <x509.crt>   Install the certificate in <file> into the local trust store. This is
                 useful for environments that live behind a corporate HTTPS proxy.

 -p <proxy>      Use the <proxy> specified as '[user:pass@]<host>:<port>'
                 items in [] are optional. It is assumed this proxy handles all protocols.

 -t <connect>    Attempt to CONNECT through the proxy using the <connect> string specified
                 as '<host>:<port>'. By default 'google.com:80' is used. Unless you block
                 access to Google (or vice versa), there's no need to change the default.

[Examples]
 Install VM guest agents and install the corporate firewall cert in certs/mitm.pem.
    $ bash bootstrap.sh -g -k certs/mitm.pem

 Quietly use nlanr.peer.local on port 80 and test the connection using EMC's webserver.
    $ bash bootstrap.sh -q -p nlanr.peer.local:80 -t emc.com:80

 Assume YES to all questions and use the proxy cache at cache.local port 3128 for HTTP-
 related traffic. Use the Docker registry at registry.local:5000 instead of DockerHub,
 and install the x509 certificate in certs/reg.pem into Docker's trust store so it can
 access the Docker registry.
    $ bash bootstrap.sh -y -p cache.local:3128 -r registry.local:5000 -d certs/reg.pem

For additional information, read the docs on GitHub.
For additional help, please open an issue on GitHub.
```

Once the archive has been expanded the installation node must be bootstrapped. To do this `cd` into the ECS-CommunityEdition directory and run `./bootstrap.sh -c deploy.yml`. Be sure to add the `-g` flag if building the ECS deployment in a virtual environment and the `-y` flag if you're okay accepting all defaults.
*Note: The bootstrap script accepts many flags. Be sure to run* `./bootsrap -h` *to see all bootstraping options.*

The bootstrapping process has completed when the following message appears:

![complete bootstrapping](../media/complete_bootstrap.png)

After the installation node has successfully bootstrapped you may be prompted to reboot the machine. If this is the case the machine must be rebooted before continuing.


### deploy.yml Basics

These steps quickly set up a basic deploy.yml file

1) Enter the IP address of the **installation node** into the `install_node` field
2) Enter CIDR address(es) of any machines authorized that will communicate with the ECS management API into the `management_clients` field. `0.0.0.0/0` Allows total access. *Note*: this may be be a block of addresses or subnet.
3) Hostnames may be auto-named with the `autonaming` field. `moons` or `cities` are options.
5) Credential configuration: usernames and credentials for node access. This must be the same across all nodes
6) Enter your DNS server address into `dns_servers`. This can be found with `cat /etc/resolv.conf`
7) Enter NTP server address into `ntp_servers`. This will likely be the same value as `dns_servers` **NOTE: this field cannot be left empty, an NTP server is required for installation.**
7) List block devices in `ecs_block_devices`.
8) Enter data node address(es) in Storage Pool `members`
1) Enter block devices again under Storage Pool `members`

*Please read the reference deploy.yml found* [here](deploy.yml.rst)*. It is designed to be self documenting and required fields are filled with either dummy or default values. The above values are only bare minimum values and may not yield the desired result.*

## Step1

Once the deploy.yml file has been correctly written the next step is to simply run `step1`. When the process begins a license agreement will appear on screen, press `q` to close the screen and type `yes` to continue or `no` to abort the process. The install cannot continue until the license agreement has been accepted.

## Step2

Once step1 has completed run `step2`

