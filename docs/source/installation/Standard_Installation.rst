Standard Installation
=====================

The standard installation assumes an Internet connected VM which will be
bootstrapped and become an install node. The ECS deployment will then
proceed from the install node.

Prerequisites
~~~~~~~~~~~~~

Listed below are all necessary components for a successful ECS Community
Edition installation. If they are not met the installation will likely
fail.

Hardware Requirements
^^^^^^^^^^^^^^^^^^^^^

The installation process is designed to be performed from either a
dedicated installation node. However, it is possible, if you so choose,
for one of the ECS data nodes to double as the install node. The install
node will bootstrap the ECS data nodes and configure the ECS instance.
When the process is complete, the install node may be safely destroyed.
Both single node and multi-node deployments require only a single
install node.

The technical requirements for the installation node are minimal, but
reducing available CPU, memory, and IO throughput will adversely affect
the speed of the installation process:

-  1 CPU Core
-  2 GB Memory
-  10 GB HDD
-  CentOS 7 Minimal installation (ISO- and network-based minimal
   installs are equally supported)

The minimum technical requirements for each ECS data node are:

-  4 CPU Cores
-  16 GB Memory
-  16 GB Minimum system block storage device
-  104 GB Minimum additional block storage device in a raw,
   unpartitioned state.
-  CentOS 7 Minimal installation (ISO- and network-based minimal
   installs are equally supported)

The recommended technical requirements for each ECS data node are:

-  8 CPU Cores
-  64GB RAM
-  16GB root block storage
-  1TB additional block storage
-  CentOS 7.4 Minimal installation

For multi-node installations each data node must fulfill these minimum
qualifications. The installer will do a pre-flight check to ensure that
the minimum qualifications are met. If they are not, the installation
will not continue.

Environmental Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^

The following environmental requirements must also be met to ensure a
successful installation:

-  **Network:** All nodes, including install node and ECS data node(s),
   must exist on the same IPv4 subnet. IPv6 networking *may* work, but
   is neither tested nor supported for ECS Community Edition at this
   time.
-  **Remote Access:** Installation is coordinated via Ansible and SSH.
   However, public key authentication during the initial authentication
   and access configuration is not yet supported. Therefore, password
   authentication must be enabled on all nodes, including install node
   and ECS data node(s). *This is a known issue and will be addressed in
   a future release*
-  **OS:** CentOS 7 Minimal installation (ISO- and network-based minimal
   installs are equally supported)

All-in-One Single-Node Deployments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A single node *can* successfully run the installation procedure on
itself. To do this simply input the node's own IP address as the
installation node as well as the data node in the deploy.yml file.

1. Getting Started
~~~~~~~~~~~~~~~~~~

It is recommended to use a non-root administrative user account with
sudo privileges on the install node when performing the deployment.
Deploying from the root account is supported, but not recommended.

Before data store nodes can be created, the install node must be
prepared. If acquiring the software via the GitHub repository, run:

0. ``cd $HOME``
1. ``sudo yum install -y git``
2. ``git clone https://github.com/EMCECS/ECS-CommunityEdition``.

If the repository is being added to the machine via usb drive, scp, or
some other file-based means, please copy the archive into ``$HOME/`` and
run:

-  for .zip archive ``unzip ECS-CommunityEdition.zip``
-  for .tar.gz archive ``tar -xzvf ECS-CommunityEdition.tar.gz``

If the directory created when unarchiving the release .zip or tarball
has a different name than ``ECS-CommunityEdition``, then rename it with
the following command:

0. ``mv <directory name> ECS-CommunityEdition``

This will help the documentation make sense as you proceed with the
deployment.

2. Creating The Deployment Map (``deploy.yml``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installation requires the creation of a deployment map. This map is
represented in a YAML configuration file called deploy.yml.

Below are steps for creating a basic deploy.yml. **All fields indicated
below are required for a successful installation.**

0. From the ``$HOME/ECS-CommunityEdition`` directory, run the commmand:
   ``cp docs/design/reference.deploy.yml deploy.yml``
1. Edit the file with your favorite editor on another machine, or use
   ``vi deploy.yml`` on the install node. Read the comments in the file
   and review the examples in the ``examples/`` directory.
2. Top-level deployment facts (``facts:``)

   0. Enter the IP address of the install node into the
      ``install_node:`` field.
   1. Enter into the ``management_clients:`` field the CIDR address/mask
      of each machine or subnet that will be whitelisted in node's
      firewalls and allowed to communicate with ECS management API.

   -  ``10.1.100.50/32`` is *exactly* the IP address.
   -  ``192.168.2.0/24`` is the entire /24 subnet.
   -  ``0.0.0.0/0`` represents the entire Internet.

3. SSH login details (``ssh_defaults:``)

   0. If the SSH server is bound to a non-standard port, enter that port
      number in the ``ssh_port:`` field, or leave it set at the default
      (22).
   1. Enter the username of a user permitted to run commands as UID
      0/GID 0 ("root") via the ``sudo`` command into the
      ``ssh_username:`` field. This must be the same across all nodes.
   2. Enter the password for the above user in the ``ssh_password:``
      field. This will only be used during the initial public key
      authentication setup and can be changed after. This must be the
      same across all nodes.

4. Node configuration (``node_defaults:``)

   0. Enter the DNS domain for the ECS installation. This can simply be
      set to ``localdomain`` if you will not be using DNS with this ECS
      deployment.
   1. Enter each DNS server address, one per line, into
      ``dns_servers:``. This can be what's present in
      ``/etc/resolv.conf``, or it can be a different DNS server
      entirely. This DNS server will be set to the primary DNS server
      for each ECS node.
   2. Enter each NTP server address, one per line, into
      ``ntp_servers:``.

5. Storage Pool configuration (``storage_pools:``)

   0. Enter the storage pool ``name:``.
   1. Enter each member data node's IP address, one per line, in
      ``members:``.
   2. Under ``options:``, enter each block device reserved for ECS, one
      per line, in ``ecs_block_devices:``. All member data nodes of a
      storage pool must be identical.

6. Virtual Data Center configuration (``virtual_data_centers:``)

   0. Enter each VDC ``name:``.
   1. Enter each member Storage Pool name, one per line, in ``members:``

7. Optional directives, such as those for Replication Groups and users,
   may also be configured at this time.
8. When you have completed the ``deploy.yml`` to your liking, save the
   file and exit the ``vi`` editor.
9. Move on to Bootstrapping

These steps quickly set up a basic deploy.yml file

More on deploy.yml
^^^^^^^^^^^^^^^^^^

If you need to make changes to your deploy.yml after bootstrapping,
there are two utilities for this.

0. The ``videploy`` utility will update the installed ``deploy.yml``
   file in place and is the preferred method.
1. The ``update_deploy`` utility will update the installed
   ``deploy.yml`` file with the contents of a different ``deploy.yml``
   file.

See the [utilties][utilities] document for more information on these and
other ECS CE utilities.

For more information on deploy.yml, please read the reference guide
found `here <deploy.yml.md>`__.

3. Bootstrapping the Install Node (``bootstrap.sh``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The bootstrap script configures the installation node for ECS deployment
and downloads the required Docker images and software packages that all
other nodes in the deployment will need for successful installation.

Once the deploy.yml file has been created, the installation node must be
bootstrapped. To do this ``cd`` into the ECS-CommunityEdition directory
and run ``./bootstrap.sh -c deploy.yml``. Be sure to add the ``-g`` flag
if building the ECS deployment in a virtual environment and the ``-y``
flag if you're okay accepting all defaults.

The bootstrap script accepts many flags. If your environment uses
proxies, including MitM SSL proxies, custom nameservers, or a local
Docker registry or CentOS mirror, you may want to indicate that on the
``bootstrap.sh`` command line.

::

    [Usage]
     -h, --help
        Display this help text and exit
     --help-build
        Display build environment help and exit
     --version
        Display version information and exit

    [General Options]
     -y / -n
        Assume YES or NO to any questions (may be dangerous).
     -v / -q
        Be verbose (also show all logs) / Be quiet (only show necessary output)
     -c <FILE>
        If you have a deploy.yml ready to go, give its path to this arg.

    [Platform Options]
     --ssh-private-key <id_rsa | id_ed25519>
     --ssh-public-key <id_rsa.pub | id_ed25519.pub>
        Import SSH public key auth material and use it when authenticating to remote nodes.
     -o, --override-dns <NS1,NS2,NS*>
        Override DHCP-configured nameserver(s); use these instead. No spaces! Use of -o is deprecated, please use --override-dns.
     -g, --vm-tools
        Install virtual machine guest agents and utilities for QEMU and VMWare. VirtualBox is not supported at this time. Use of -g is deprecated, please use --vm-tools.
     -m, --centos-mirror <URL>
        Use the provided package <mirror> when fetching packages for the base OS (but not 3rd-party sources, such as EPEL or Debian-style PPAs). The mirror is specified as '<host>:<port>'. This option overrides any mirror lists the base OS would normally use AND supersedes any proxies (assuming the mirror is local), so be warned that when using this option it's possible for bootstrapping to hang indefinitely if the mirror cannot be contacted. Use of -m is deprecated, please use --centos-mirror.

    [Docker Options]
     -r, --registry-endpoint REGISTRY
        Use the Docker registry at REGISTRY instead of DockerHub. The connect string is specified as '<host>:<port>[/<username>]'. You may be prompted for your credentials if authentication is required. You may need to use -d (below) to add the registry's cert to Docker. Use of -r is deprecated, please use --registry-endpoint.

     -l, --registry-login
        After Docker is installed, login to the Docker registry to access images which require access authentication. This will authenticate with Dockerhub unless --registry-endpoint is also used. Use of -l is deprecated, please use --registry-login.

     -d, --registry-cert <FILE>
        [Requires --registry-endpoint] If an alternate Docker registry was specified with -r and uses a cert that cannot be resolved from the anchors in the local system's trust store, then use -d to specify the x509 cert file for your registry.

    [Proxies & Middlemen]
     -p, --proxy-endpoint <PROXY>
        Connect to the Internet via the PROXY specified as '[user:pass@]<host>:<port>'. Items in [] are optional. It is assumed this proxy handles all protocols.  Use of -p is deprecated, please use --proxy-endpoint.
     -k, --proxy-cert <FILE>
        Install the certificate in <file> into the local trust store. This is useful for environments that live behind a corporate HTTPS proxy.  Use of -k is deprecated, please use --proxy-cert.
     -t, --proxy-test-via <HOSTSPEC>
        [Requires --proxy-endpoint] Test Internet connectivity through the PROXY by connecting to HOSTSPEC. HOSTSPEC is specified as '<host>:<port>'. By default 'google.com:80' is used. Unless access to Google is blocked (or vice versa), there is no need to change the default.

    [Examples]
     Install VM guest agents and use SSH public key auth keys in the .ssh/ directory.
        $ bash bootstrap.sh --vm-tools --ssh-private-key .ssh/id_rsa --ssh-public-key .ssh/id_rsa.pub

     Quietly use nlanr.peer.local on port 80 and test the connection using EMC's webserver.
        $ bash bootstrap.sh -q --proxy-endpoint nlanr.peer.local:80 -proxy-test-via emc.com:80

     Assume YES to all questions. Use the CentOS mirror at http://cache.local/centos when fetching packages. Use the Docker registry at registry.local:5000 instead of DockerHub, and install the x509 certificate in certs/reg.pem into Docker's trust store so it can access the Docker registry.
        $ bash bootstrap.sh -y --centos-mirror http://cache.local/centos --registry-endpoint registry.local:5000 --registry-cert certs/reg.pem

The bootstrapping process has completed when the following message
appears:

::

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

After the installation node has successfully bootstrapped you will
likely be prompted to reboot the machine. If so, then the machine MUST
be rebooted before continuing to Step 4.

4. Deploying ECS Nodes (``step1``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the deploy.yml file has been correctly written and the install node
rebooted if needed, then the next step is to simply run ``step1``.

After the installer initializes, the EMC ECS license agreement will
appear on the screen. Press ``q`` to close the screen and type ``yes``
to accept the license and continue or ``no`` to abort the process. The
install cannot continue until the license agreement has been accepted.

5. Deploying ECS Topology (``step2``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*If you would prefer to manually configure your ECS topology, you may
skip this step entirely.*

Once ``step1`` has completed, you may then direct the installer to
configure the ECS topology by running ``step2``. Once ``step2`` has
completed, your ECS will be ready for use.

That's it!
----------

Assuming all went well, you now have a functioning ECS Community Edition
instance and you may now proceed with your test efforts.
