OVA Installation
================

The OVA installation assumes deployment in a network-isolated
environment. One clone of the OVA will become an install node. The ECS
deployment will then proceed from the install node.

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

1.1. Download and deploy the OVA to a VM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OVA is available for download from `the release notes
page <https://github.com/EMCECS/ECS-CommunityEdition/releases>`__.
Select the most recent version of the OVA for the best experience.

1.2. Deploy a VM from the OVA and Adjust its resources to have a minimum of:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  16GB RAM
-  4 CPU cores
-  (Optional) Increase vmdk from the minimum 104GB

1.3. Clone the VM
^^^^^^^^^^^^^^^^^

Clone the VM you created enough times to reach the number of nodes
desired for your deployment. The minimum number of nodes for basic
functionality is one (1). The minimum number of nodes for erasure coding
replication to be enabled is four (4).

1.4. Collect and Configure networking information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Power on the VMs and collect their DHCP assigned IP addresses from the
vCenter client or from the VMs themselves

You may also assign static IP addresses by logging into each VM and
running ``nmtui`` to set network the network variables (IP, mask,
gateway, DNS, etc).

The information you collect in this step is crucial for step 2.

2. Creating The Deployment Map (``deploy.yml``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installation requires the creation of a deployment map. This map is
represented in a YAML configuration file called deploy.yml.

Below are steps for creating a basic deploy.yml. **All fields indicated
below are required for a successful installation.**

0. Log into the first VM and run ``videploy``.
1. Edit this deploy.yml file with your favorite editor on another
   machine, or use ``vi deploy.yml`` on the install node. Read the
   comments in the file and review the examples in the ``examples/``
   directory.
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
8. After completing the deploy.yml file to your liking, exit out of
   ``videploy`` as you would the ``vim`` editor (ESC, :, wq, ENTER).
   This will update the deploy.yml file.

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

4. Deploying ECS Nodes (``ova-step1``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the deploy.yml file has been correctly written and the install node
rebooted if needed, then the next step is to simply run ``ova-step1``.

After the installer initializes, the EMC ECS license agreement will
appear on the screen. Press ``q`` to close the screen and type ``yes``
to accept the license and continue or ``no`` to abort the process. The
install cannot continue until the license agreement has been accepted.

5. Deploying ECS Topology (``ova-step2``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*If you would prefer to manually configure your ECS topology, you may
skip this step entirely.*

Once ``ova-step1`` has completed, you may then direct the installer to
configure the ECS topology by running ``ova-step2``. Once ``ova-step2``
has completed, your ECS will be ready for use.

That's it!
----------

Assuming all went well, you now have a functioning ECS Community Edition
instance and you may now proceed with your test efforts.
