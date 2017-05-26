# ECS Community Edition Installation

ECS Community Edition now features a brand new installer. This installer aims to greatly improve user experience through automation. This document will guide the user through the new installation process.

## Prerequisites

Listed below are all necessary components for a successful ECS Community Edition installation. If they are not met the installation will likely fail.

### Hardware Requirements

The installation process is designed to be performed from either a dedicated installation node. However, it is possible, if you so choose, for one of the ECS data nodes to double as the install node.  The install node will bootstrap the ECS data nodes and configure the ECS instance. When the process is complete, the install node may be safely destroyed. Both single node and multi-node deployments require only a single install node.

The technical requirements for this machine are minimal, but reducing available CPU, memory, and IO throughput will adversely affect the speed of the installation process:

* 1 CPU Core
* 2 GB Memory
* 10 GB HDD
* CentOS 7 Minimal installation (ISO- and network-based minimal installs are equally supported)

The minimum technical requirements for each ECS data node are:

* 4 CPU Cores
* 16 GB Memory
* 16 GB Minimum system block storage device
* 104 GB Minimum additional block storage device in a raw, unpartitioned state.
* CentOS 7 Minimal installation (ISO- and network-based minimal installs are equally supported)

The recommended technical requirements for each ECS data node are:

* 8 CPU Cores
* 64GB RAM
* 16GB root block storage
* 1TB additional block storage
* CentOS 7.3 Minimal installation

For multi-node installations each data node must fulfill these minimum qualifications. The installer will do a pre-flight check to ensure that the minimum qualifications are met. If they are not, the installation will not continue.

### Environmental Requirements

The following environmental requirements must also be met to ensure a successful installation:

* **Network:** All nodes, including install node and ECS data node(s), must exist on the same IPv4 subnet.  IPv6 networking *may* work, but is neither tested nor supported for ECS Community Edition at this time.
* **Remote Access:** Installation is coordinated via Ansible and SSH. However, public key authentication during the initial authentication and access configuration is not yet supported.  Therefore, password authentication must be enabled on all nodes, including install node and ECS data node(s).  *This is a known issue and will be addressed in a future release*
* **OS:** CentOS 7 Minimal installation (ISO- and network-based minimal installs are equally supported)

### Install Node Data Nodes

A single node *can* successfully run the installation procedure on itself. To do this simply input the node's own IP address as the installation node as well as the data node in the deploy.yml file.

## 1. Getting Started

Before the data nodes can be created the install node must be prepared. If downloading the repository from github run `sudo yum install git -y` to install git and then `git clone https://github.com/EMCECS/ECS-CommunityEdition`. If the repository is being added to the machine via usb drive, scp, or some other file-based means. run:

* for .zip archive `unzip ECS-CommunityEdition.zip`
* for .tar.gz archive `tar -xzvf ECS-CommunityEdition.tar.gz`

## 2. Creating The Deployment Map (`deploy.yml`)

Installation requires the creation of a deployment map. This map is represented in a YAML configuration file called deploy.yml. This file *should* be written before moving on for the smoothest experience, but there is a deployment path for creating deploy.yml after bootstrapping the Install Node.

Create this file in the `ECS-CommunityEdition` directory that was created when the repository was cloned. A template guide for writing this file can be found [here](deploy.yml.rst).

Below are steps for creating a basic deploy.yml. **Please note that all fields mentioned below are required for a successful installation.**

0. From the ECS-CommunityEdition directory, run the commmand: `cp docs/design/reference.deploy.yml deploy.yml`
0. Edit the file with your favorite editor on another machine, or use `vi deploy.yml` on the Install Node.  Read the comments in the file and review the examples in the `examples/` directory.
0. Top-level deployment facts (`facts:`)
    0. Enter the IP address of the Install Node into the `install_node:` field.
    0. Enter into the `management_clients:` field the CIDR address/mask of each machine or subnet that will be whitelisted in node's firewalls and allowed to communicate with ECS management API.
      * `10.1.100.50/32` is *exactly* the IP address.
      * `192.168.2.0/24` is the entire /24 subnet.
      * `0.0.0.0/0` represents the entire Internet.
0. SSH login details (`ssh_defaults:`)
    0. If the SSH server is bound to a non-standard port, enter that port number in the `ssh_port:` field, or leave it set at the default (22).
    0. Enter the username of a user permitted to run commands as UID 0/GID 0 ("root") via the `sudo` command into the `ssh_username:` field. This must be the same across all nodes.
    0. Enter the password for the above user in the `ssh_password:` field. This will only be used during the initial public key authentication setup and can be changed after.  This must be the same across all nodes.
0. Node configuration (`node_defaults:`)
    0. Enter the DNS domain for the ECS installation.  This can simply be set to `localdomain` if you will not be using DNS with this ECS deployment.
    0. Enter each DNS server address, one per line, into `dns_servers:`. This can be what's present in `/etc/resolv.conf`, or it can be a different DNS server entirely.  This DNS server will be set to the primary DNS server for each ECS node.
    0. Enter each NTP server address, one per line, into `ntp_servers:`.
0. Storage Pool configuration (`storage_pools:`)
    0. Enter the storage pool `name:`.
    0. Enter each member data node address, one per line, in `members:`.
    0. Under `options:`, enter each block device reserved for ECS, one per line, in `ecs_block_devices:`.
0. Virtual Data Center configuration (`virtual_data_centers:`)
    0. Enter the VDC `name:`.
    0. Enter each member Storage Pool name, one per line, in `members:`
0. When you have completed the `deploy.yml` to your liking, save the file and exit the `vi` editor.
0. Move on to Bootstrapping

These steps quickly set up a basic deploy.yml file

#### More on deploy.yml
Please read the reference deploy.yml found [here](http://ecs-community-edition.readthedocs.io/en/latest/installation/deploy.yml.html). It is designed to be self documenting and required fields are filled with either example or default values. The above values are only bare minimum values and may not yield optimal results for your environment.

## 3. Bootstrapping the Install Node (`bootstrap.sh`)

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

 -m <mirror>     Use the provided package <mirror> when fetching packages for the
                 base OS (but not 3rd-party sources, such as EPEL or Debian-style PPAs).
                 The mirror is specified as '<host>:<port>'. This option overrides any
                 mirror lists the base OS would normally use AND supersedes any proxies
                 (assuming the mirror is local), so be warned that when using this
                 option it's possible for bootstrapping to hang indefinitely if the
                 mirror cannot be contacted.

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
    $ ./bootstrap.sh -g -k certs/mitm.pem

 Quietly use nlanr.peer.local on port 80 and test the connection using EMC's webserver.
    $ ./bootstrap.sh -q -p nlanr.peer.local:80 -t emc.com:80

 Assume YES to all questions and use the proxy cache at cache.local port 3128 for HTTP-
 related traffic. Use the Docker registry at registry.local:5000 instead of DockerHub,
 and install the x509 certificate in certs/reg.pem into Docker's trust store so it can
 access the Docker registry.
    $ ./bootstrap.sh -y -p cache.local:3128 -r registry.local:5000 -d certs/reg.pem
```

Once the archive has been expanded the installation node must be bootstrapped. To do this `cd` into the ECS-CommunityEdition directory and run `./bootstrap.sh -c deploy.yml`. Be sure to add the `-g` flag if building the ECS deployment in a virtual environment and the `-y` flag if you're okay accepting all defaults.
*Note: The bootstrap script accepts many flags. Be sure to run* `./bootsrap -h` *to see all bootstraping options.*

The bootstrapping process has completed when the following message appears:

```
> All done bootstrapping your install node.
>
> To continue (after reboot if needed):
>     $ cd /home/admin/ECS-CommunityEdition
> If you have a deploy.yml ready to go (and did not use -c flag):
>     $ sudo cp deploy.yml /opt/emc/ecs-install/
> If not, check out the docs/design and examples directory for references.
> Once you have a deploy.yml, you can start the deployment
> by running:
>
> [WITH Internet access]
>     $ step1
>   [Wait for deployment to complete, then run:]
>     $ step2
>
> [WITHOUT Internet access]
>     $ island-step1
>   [Migrate your install node into the isolated environment and run:]
>     $ island-step2
>   [Wait for deployment to complete, then run:]
>     $ island-step3
>
```

After the installation node has successfully bootstrapped you may be prompted to reboot the machine. If this is the case the machine must be rebooted before continuing.

## 4. Deploying ECS Nodes (`step1` or `island-step1`)

Once the deploy.yml file has been correctly written the next step is to simply run one of the following commands:
* Internet-connected environments: `step1`
* Island environments: `island-step1`

After the installer initializes, the EMC ECS license agreement will appear on the screen. Press `q` to close the screen and type `yes` to accept the license and continue or `no` to abort the process. The install cannot continue until the license agreement has been accepted.

The first thing the installer will do is create an artifact cache of base operating system packages and the ECS software Docker image.  If you are running `step1`, then you may move on to **4.5**.  If you are running `island-step1`, then the installer will stop after this step.  The install node can then be migrated into your island environment where deployment can continue.

### 4.4 Deploying the ECS Nodes (`island-step2`)

* Internet-connected environments: *automatic*
* Island environments: `island-step2`

If you are deploying to Internet-connected nodes and used `step1` to begin your deployment, then this section is informational only and you may move on to **5**.  If you are deploying into an island environment and have migrated the install node into your island, you can begin this process by running `island-step2`.  The next tasks the installer will perform are: configuring the ECS nodes, performing a pre-flight check to ensure ECS nodes are viable deployment targets, distributing the artifact cache to ECS nodes, installing necessary packages, and finally deploying the ECS software and init scripts onto ECS nodes.

## 5. Deploying ECS Topology (`step2` or `island-step3`)

* Internet-connected environments: `step2`
* Island environments: `island-step3`

Once either `step1` or `island-step2` have completed, you may then direct the installer to configure the ECS topology by running either `step2` or `island-step3`.  These commands are identical.  Once `step2` or `island-step3` have completed, your ECS will be ready for use.
If you would prefer to manually configure your ECS topology, you may skip this step entirely.
