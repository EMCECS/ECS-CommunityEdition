```
# deploy.yml reference implementation

# By changing the license_accepted boolean value to "true" you are
# declaring your agreement to the terms of the license agreement
# contained in the license.txt file included with this software
# distribution.
licensing:
  license_accepted: false

# Deployment facts reference
facts:

  # [Required]
  # Node IP or resolvable hostname from which installations will be launched
  # The only supported configuration is to install from the same node as the
  # bootstrap.sh script is run.
  # NOTE: if the install node is to be migrated into an island environment,
  #       the hostname or IP address listed here should be the one in the
  #       island environment.
  install_node: 192.168.2.200

  # [Required]
  # IPs of machines that will be whitelisted in the firewall and allowed
  # to access management ports of all nodes.  If this is set to the
  # wildcard (0.0.0.0/0) then anyone can access management ports.
  management_clients:
    - 0.0.0.0/0

  # [Optional]
  # Picklist for node names.
  # Available options:
  # - "moons" (ECS CE default)
  # - "cities" (ECS SKU-flavored)
  autonaming: moons

  # *** IMPORTANT ***
  # [Required]
  # These credentials must be the same across all nodes.  Ansible uses these credentials to
  # gain initial access to each node in the deployment and set up ssh public key authentication.
  # If these are not correct, the deployment WILL fail.
  ansible_defaults:
    # Username to login as
    ansible_user: admin
    # Password to use with SSH login
    ansible_ssh_pass: ChangeMe
    # Password to use with other challenges
    ansible_password: ChangeMe
    # Password to use with sudo to become root
    ansible_become_pass: ChangeMe

  # [Required]
  # Environment configuration for this deployment.
  # Unless you have a custom ECS for which the default credentials have been changed,
  # ecs_root_user and ecs_root_pass must be set to "root" and "ChangeMe" respectively.
  node_defaults:
    ecs_root_user: root
    ecs_root_pass: ChangeMe
    dns_domain: local
    dns_servers:
      - 192.168.2.2
    ntp_servers:
      - 192.168.2.2

  # [Required]
  # Storage pool defaults. Configure to your liking.
  # All block devices that will be consumed by ECS on ALL nodes must be listed under the
  # ecs_block_devices option.  This can be overridden by the storage pool configuration.
  # At least ONE (1) block device is REQUIRED for a successful install.  More is better.
  storage_pool_defaults:
    is_cold_storage_enabled: false
    is_protected: false
    description: Default storage pool description
    ecs_block_devices:
      - /dev/vda

  # [Required]
  # Storage pool layout.  You MUST have at least ONE (1) storage pool for a successful install.
  storage_pools:
    - name: sp1
      members:
        - 192.168.2.220
        - 192.168.2.221
      options:
        description: My First SP
        ecs_block_devices:
          - /dev/vda
    - name: sp2
      members:
        - 192.168.2.222
        - 192.168.2.223
      options:
        is_protected: false
        is_cold_storage_enabled: false
        description: My Second SP

  # [Required]
  # VDC defaults.  Configure to your liking.
  virtual_data_center_defaults:
    description: Default virtual data center description

  # [Required]
  # Virtual data center layout.  You MUST have at least ONE (1) VDC for a successful install.
  # Multi-VDC deployments are not yet implemented
  virtual_data_centers:
    - name: vdc1
      members:
        - sp1
      options:
        description: My First VDC
    - name: vdc2
      members:
        - sp2
      options:
        description: My Second VDC

  # [Required]
  # Replication group defaults.  Configure to your liking.
  replication_group_defaults:
    description: Default replication group description
    enable_rebalancing: true
    allow_all_namespaces: true
    is_full_rep: false

  # [Required]
  # Replication group layout.  You MUST have at least ONE (1) RG for a successful install.
  replication_groups:
    - name: rg1
      members:
        - vdc1
      options:
        description: My First RG
    - name: rg2
      members:
        - vdc2
      options:
        description: My Second RG
    - name: rg-global
      members:
        - vdc1
        - vdc2
      options:
        description: My Global RG

# [Required]
# Namespace configuration is not yet implemented
  # Namespace defaults.
#  namespace_defaults:
#    is_stale_allowed: false
#    is_compliance_enabled: false
#    is_encryption_enabled: false
#    namespace_admins: root

# [Required]
  # Namespace layout (optional)
#  namespaces:
#    - name: ns1
#      members:
#        - rg1
#      options:
#        description: My First Namespace

# [Required]
# User configuration is not yet implemented
  # User defaults.
#  user_defaults:
#    namespace: ns1
#    tags:
#      - my
#      - default
#      - usertags

# [Required]
  # User layout (optional)
#  users:
#    - name: user1
#      namespace: ns1
#      tags:
#        - iamauser

# [Required]
# Bucket configuration is not yet implemented
  # Bucket defaults.
#  bucket_defaults:
#    namespace: ns1
#    admin_users:
#      - root

# [Required]
  # Bucket layout (optional)
#  buckets:
#    - name: bucket1
#      namespace: ns1
#      options:
#        admin_users:
#          - root



```