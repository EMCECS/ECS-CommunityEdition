ECS Community Edition Utilities
===============================

``ecsdeploy``
-------------

The ``ecsdeploy`` utility responsible for executing Ansible playbooks
and helper scripts responsible for deploying ECS Community Edition to
member data nodes.

::

    Usage: ecsdeploy [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

      Command line interface to ecs-install installer

    Options:
      -v, --verbose  Use multiple times for more verbosity
      --help         Show this message and exit.

    Commands:
      access         Configure ssh access to nodes
      bootstrap      Install required packages on nodes
      cache          Build package cache
      check          Check data nodes to ensure they are in compliance
      deploy         Deploy ECS to nodes
      disable-cache  Disable datanode package cache handling
      enable-cache   Enable datanode package cache handling
      load           Apply deploy.yml
      reboot         Reboot data nodes that need it
      start          Start the ECS service
      stop           Stop the ECS service

``ecsconfig``
-------------

The ``ecsconfig`` utility responsible for communicating with the ECS
management API and configuring an ECS deployment with administrative and
organizational objects.

::

    Usage: ecsconfig [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

      Command line interface to configure ECS from declarations in deploy.yml

    Options:
      -v, --verbose  Use multiple times for more verbosity
      --help         Show this message and exit.

    Commands:
      licensing        Work with ECS Licenses
      management-user  Work with ECS Management Users
      namespace        Work with ECS Namespaces
      object-user      Work with ECS Object Users
      ping             Check ECS Management API Endpoint(s)
      rg               Work with ECS Replication Groups
      sp               Work with ECS Storage Pools
      trust            Work with ECS Certificates
      vdc              Work with ECS Virtual Data Centers

``ecsremove``
-------------

The ``ecsremove`` utility is responsible for removing ECS instances and
artifacts from member data nodes and the install node.

::

    Usage: ecsremove [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

      Command line interface to remove ECS bits

    Options:
      -v, --verbose  Use multiple times for more verbosity
      --help         Show this message and exit.

    Commands:
      purge-all        Uninstall ECS and purge artifacts from all nodes
      purge-installer  Purge caches from install node
      purge-nodes      Uninstall ECS and purge artifacts from data nodes

``enter``
---------

This utility has two functions: 1. To access member data nodes by name
``enter luna`` 2. To access the ``ecs-install`` image directly and the
contents of the data container.

Accessing the ``ecs-install`` image directly

::

    [admin@installer-230 ~]$ enter
    installer-230 [/]$

Accessing a member node

::

    [admin@installer-230 ~]$ enter luna
    Warning: Identity file /opt/ssh/id_ed25519 not accessible: No such file or directory.
    Warning: Permanently added 'luna,192.168.2.220' (ECDSA) to the list of known hosts.
    Last login: Thu Nov  9 16:44:31 2017 from 192.168.2.200
    [admin@luna ~]$

``catfacts``
------------

This utility displays all the facts Ansible has registered about a node
in pretty-printed, colorized output from ``jq`` paged through ``less``.

Running ``catfacts`` without an argument lists queryable nodes.

::

    [admin@installer-230 ~]$ catfacts
    Usage: $ catfacts <Ansible inventory host>
    Here is a list of hosts you can query:
    Data Node(s):
      hosts (1):
        192.168.2.220
    Install Node:
      hosts (1):
        192.168.2.200

Querying a node

::

    [admin@installer-230 ~]$ catfacts 192.168.2.200
    {
      "ansible_all_ipv4_addresses": [
        "172.17.0.1",
        "192.168.2.200"
      ],
      "ansible_all_ipv6_addresses": [
        "fe80::42:98ff:fe85:2502",
        "fe80::f0c5:a7d1:6fff:205e"
      ],
      "ansible_apparmor": {
        "status": "disabled"
      },
      "ansible_architecture": "x86_64",
      "ansible_bios_date": "04/01/2014",
      "ansible_bios_version": "rel-1.8.2-0-g33fbe13 by qemu-project.org",
      "ansible_cmdline": {
        "BOOT_IMAGE": "/vmlinuz-3.10.0-693.5.2.el7.x86_64",
        "LANG": "en_US.UTF-8",

    [... snip ...]

``update_deploy``
-----------------

This utility updates the ``/opt/emc/ecs-install/deploy.yml`` file with
the updated contents of the file ``deploy.yml`` provided during
bootstrapping. It can also set the path to the ``deploy.yml`` file from
which to fetch updates.

Running with no arguments

::

    [admin@installer-230 ~]$ update_deploy
    > Updating /opt/emc/ecs-install/deploy.yml from /home/admin/ecsce-lab-configs/local/local-lab-1-node-1/deploy.yml
    37c37
    <     ssh_password: ChangeMe
    ---
    >     ssh_password: admin
    > Recreating ecs-install data container
    ecs-install> Initializing data container, one moment ... OK
    ecs-install> Applying deploy.yml

Updating the deploy.yml file to a different source.

::

    [admin@installer-230 ~]$ update_deploy ~/ecsce-lab-configs/local/local-lab-1-node-2/deploy.yml
    > Updating bootstrap.conf to use deploy config from /home/admin/ecsce-lab-configs/local/local-lab-1-node-2/deploy.yml
    > Updating /opt/emc/ecs-install/deploy.yml from /home/admin/ecsce-lab-configs/local/local-lab-1-node-2/deploy.yml
    37c37
    <     ssh_password: admin
    ---
    >     ssh_password: ChangeMe
    82c82
    <         - 192.168.2.221
    ---
    >         - 192.168.2.220
    173a174
    >
    > Recreating ecs-install data container
    ecs-install> Initializing data container, one moment ... OK
    ecs-install> Applying deploy.yml

``videploy``
------------

This utility modifies the ``deploy.yml`` file currently installed at
``/opt/emc/ecs-install/deploy.yml``.

::

    [admin@installer-230 ~]$ videploy

First, vim runs with the contents of ``deploy.yml``, and then
``videploy`` calls ``update_deploy``.

``pingnodes``
-------------

This utility pings nodes involved in the deployment using Ansible's
``ping`` module to verify connectivity. It can be used to ping groups or
individual nodes.

Ping all data nodes (default)

::

    [admin@installer-230 ~]$ pingnodes
    192.168.2.220 | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }

Ping all known nodes

::

    [admin@installer-230 ~]$ pingnodes all
    localhost | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }
    192.168.2.200 | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }
    192.168.2.220 | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }

Ping the node identified as 192.168.2.220

::

    [admin@installer-230 ~]$ pingnodes 192.168.2.220
    192.168.2.220 | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }

Ping members of the install\_node group

::

    [admin@installer-230 ~]$ pingnodes install_node
    192.168.2.200 | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }

``inventory``
-------------

This utility displays the known Ansible inventory and all registered
group and host variables.

::

    [admin@installer-230 ~]$ inventory
    {
      "ecs_install": {
        "hosts": [
          "localhost"
        ],
        "vars": {
          "ansible_become": false,
          "ansible_python_interpreter": "/usr/local/bin/python",
          "ansible_connection": "local"
        }
      },
      "install_node": {
        "hosts": [
          "192.168.2.200"
        ],

    [... snip ...]
