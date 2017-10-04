# ECS Community Edition Installation

## Standard Installation

ECS Community Edition now features a brand new installer. This installer aims to greatly improve user experience through automation. This document will guide the user through the new installation process.

### Prerequisites

Listed below are all necessary components for a successful ECS Community Edition installation. If they are not met the installation will likely fail.

#### Hardware Requirements

The installation process is designed to be performed from either a dedicated installation node. However, it is possible, if you so choose, for one of the ECS data nodes to double as the install node.  The install node will bootstrap the ECS data nodes and configure the ECS instance. When the process is complete, the install node may be safely destroyed. Both single node and multi-node deployments require only a single install node.

The technical requirements for the installation node are minimal, but reducing available CPU, memory, and IO throughput will adversely affect the speed of the installation process:

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

#### Environmental Requirements

The following environmental requirements must also be met to ensure a successful installation:

* **Network:** All nodes, including install node and ECS data node(s), must exist on the same IPv4 subnet.  IPv6 networking *may* work, but is neither tested nor supported for ECS Community Edition at this time.
* **Remote Access:** Installation is coordinated via Ansible and SSH. However, public key authentication during the initial authentication and access configuration is not yet supported.  Therefore, password authentication must be enabled on all nodes, including install node and ECS data node(s).  *This is a known issue and will be addressed in a future release*
* **OS:** CentOS 7 Minimal installation (ISO- and network-based minimal installs are equally supported)

#### All-in-One Single-Node Deployments

A single node *can* successfully run the installation procedure on itself. To do this simply input the node's own IP address as the installation node as well as the data node in the deploy.yml file.

### 1. Getting Started

Please use a non-root administrative user account with sudo privileges on the Install Node when performing the deployment.  If deploying from the provided OVA, this account is username `admin` with password `ChangeMe`.

Before data store nodes can be created, the install node must be prepared. If downloading the repository from github run the following commands to get started:

0. `sudo yum install -y git`
0. `git clone https://github.com/EMCECS/ECS-CommunityEdition`.

If the repository is being added to the machine via usb drive, scp, or some other file-based means, please copy the archive into `$HOME/` and run:

* for .zip archive `unzip ECS-CommunityEdition.zip`
* for .tar.gz archive `tar -xzvf ECS-CommunityEdition.tar.gz`

###### Important Note
> This documentation refers only to the `ECS-CommunityEdition` directory, but the directory created when unarchiving the release archive may have a different name than `ECS-CommunityEdition`.  If this is so, please rename the directory created to `ECS-CommunityEdition` with the `mv` command.  This will help the documentation make sense as you proceed with the deployment.

### 2. Creating The Deployment Map (`deploy.yml`)
###### Important Note
> When installing using the OVA method, please run `videploy` at this time and skip to Step 2.2.

Installation requires the creation of a deployment map. This map is represented in a YAML configuration file called deploy.yml. This file *should* be written before the next step for the smoothest experience.

##### 2.1
Create this file in the `ECS-CommunityEdition` directory that was created when the repository was cloned. A template guide for writing this file can be found [here](deploy.yml).

##### 2.2
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
    0. Enter each VDC `name:`.
    0. Enter each member Storage Pool name, one per line, in `members:`
0. Optional directives, such as those for Replication Groups and users, may also be configured at this time.
0. When you have completed the `deploy.yml` to your liking, save the file and exit the `vi` editor.
0. Move on to Bootstrapping

These steps quickly set up a basic deploy.yml file

##### More on deploy.yml
Please read the reference deploy.yml found [here](deploy.yml). It is designed to be self documenting and required fields are filled with either example or default values. The above values are only bare minimum values and may not yield optimal results for your environment.

### 3. Bootstrapping the Install Node (`bootstrap.sh`)
###### Important Note
>When installing using the OVA method, please skip to Step 4.

The bootstrap script configures the installation node for ECS deployment and downloads the required Docker images and software packages that all other nodes in the deployment will need for successful installation.

Once the deploy.yml file has been created, the installation node must be bootstrapped. To do this `cd` into the ECS-CommunityEdition directory and run `./bootstrap.sh -c deploy.yml`. Be sure to add the `-g` flag if building the ECS deployment in a virtual environment and the `-y` flag if you're okay accepting all defaults.

The bootstrap script accepts many flags. If your environment uses proxies, including MitM SSL proxies, custom nameservers, or a local Docker registry or CentOS mirror, you may want to indicate that on the `bootstrap.sh` command line.

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

 -l              After Docker is installed, login to the Docker registry to access images
                 which require access authentication. Login to Dockerhub by default unless
                 -r is used.

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

After the installation node has successfully bootstrapped you may be prompted to reboot the machine. If so, then the machine must be rebooted before continuing to Step 4.

### 4. Deploying ECS Nodes (`step1` or `island-step1`)

Once the deploy.yml file has been correctly written and the Install Node rebooted if needed, then the next step is to simply run one of the following commands:

* Internet-connected environments: `step1`
* Island environments: `island-step1`

After the installer initializes, the EMC ECS license agreement will appear on the screen. Press `q` to close the screen and type `yes` to accept the license and continue or `no` to abort the process. The install cannot continue until the license agreement has been accepted.

The first thing the installer will do is create an artifact cache of base operating system packages and the ECS software Docker image.  If you are running `step1`, please skip to **Step 5**.  If you are running `island-step1`, then the installer will stop after this step.  The install node can then be migrated into your island environment where deployment can continue.

##### 4.5. Deploying the Island Environment ECS Nodes (`island-step2`)
###### Important Note
> If you are deploying to Internet-connected nodes and used `step1` to begin your deployment, please skip to **Step 5**.

* Internet-connected environments: *automatic*
* Island environments: `island-step2`

If you are deploying into an island environment and have migrated the install node into your island, you can begin this process by running `island-step2`.  The next tasks the installer will perform are: configuring the ECS nodes, performing a pre-flight check to ensure ECS nodes are viable deployment targets, distributing the artifact cache to ECS nodes, installing necessary packages, and finally deploying the ECS software and init scripts onto ECS nodes.

### 5. Deploying ECS Topology (`step2` or `island-step3`)

* Internet-connected environments: `step2`
* Island environments: `island-step3`

Once either `step1` or `island-step2` have completed, you may then direct the installer to configure the ECS topology by running either `step2` or `island-step3`.  These commands are identical.  Once `step2` or `island-step3` have completed, your ECS will be ready for use.
If you would prefer to manually configure your ECS topology, you may skip this step entirely.

## OVA Installation

ECS Community Edition can optionally be installed with the OVA available [on the release notes page](https://github.com/EMCECS/ECS-CommunityEdition/releases). To install with this method:

### 1. Download and deploy the OVA to a VM

### 2. Adjust the resources to have a minimum of:

    * 16GB RAM
    * 4 CPU cores
    * (Optional) Increase vmdk from the minimum 104GB

### 3. Clone VM to number of nodes desired

### 4. Collect network information

Power on VM's and collect their DHCP assigned IP addresses from the vCenter client or from the VMs themselves

You may also assign static IP addresses by logging into each VM and running `nmtui` to set network the network variables (IP, mask, gateway, DNS, etc).

### 5. Log into the first VM and run `videploy`

Follow the directions laid out in the standard installation concerning the creation of the deploy.yml file (section 2).

After completing the deploy.yml file, exit out of `videploy`, this will update the deploy.yml file.

### 6. Run `step1`

### 7. Run `step2`

###### Important Note: `step1` and `step2` are not scripts and should not be run as such. `./step1` is not a valid command.


## That's it!
Assuming all went well, you now have a functioning ECS Community Edition instance and you may now proceed with your test efforts.
