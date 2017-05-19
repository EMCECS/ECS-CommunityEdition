# Deployment Example: Travis's Desktop All-in-One (single-node) Lab-in-a-Box
In this configuration example, a single-node ECS CE will be deployed in on the same VM as the installer, creating a true single-node deployment. The node is a larger VM (16GB RAM and 500GB extra block storage).

## Arguments to the Bootstrap Script
In `bootstrap-local.sh` you'll find a shortcut to `bootstrap.sh` with all the options this configuration example wants to use:

```
./bootstrap.sh -y -g -r cache.local:5000 -d examples/local-lab-1-node/registry.crt -p cache.local:3128 -m cache.local -c examples/local-lab-all-in-one/deploy.yml
```

_That's a lot of arguments!_  Let's look at what each of them does:

| Arg | Description |
| ---- | ----------- |
| `-y` | Tells `bootstrap.sh` that I want it to assume yes to any question it might have for me. This is handy because it will automatically reboot the install node if it the install node wants to reboot after updates. |
| `-g` | The lab VMs are running under the **kvm-qemu** hypervisor, so I want to install the QEMU guest additions. There are also **VMWare** guest additions available via the open-vm-tools package. The bootstrap script installs all guest additions it knows about when this flag is given because the guest addition daemons are smart enough to know when they aren't needed. |
| `-r` | I have store all the Docker images I use frequently in my local docker registry, `cache.local:5000`, so I specify that registry using the `-r` flag. |
| `-d` | My Docker registry uses a self-signed cert, so I have to import it into the Docker trust store (or else Docker will throw an identity error). |
| `-p` | As much as possible I try to speed things up with local caches, Docker registries, OS package mirrors, etc. Here the `-p` flag tells `bootstrap.sh` to use my Squid proxycache running on `cache.local:3128`. |
| `-m` | This points to my local CentOS mirror. |
| `-c` | And finally, I have a deploy.yml already built for this lab, so I can tell `bootstrap.sh` to import it now so I don't have to do it later. |

## Deployment Config File: deploy.yml
Deployment configuration for ECS Community Edition can be boiled down to a single YAML file, `deploy.yml`.  Deployment details can be tuned by making changes to the file provided using the `-c` argument to `bootstrap.sh` and running `update_deploy` to reload the deployment profile.

The deployment system uses [Ansible](https://github.com/ansible/ansible) to get most things done, and you'll notice a few Ansible-specific variables directly referenced in `deploy.yml`.   The `ansible_user` variable needs to be set to a user on the node with `sudo` access.  In this case I'm using a user generically-named "admin" on my lab VMs.  The `ansible_*_pass` variables need to be set to admin's password.  Ansible needs to know the password so it can login and update `$HOME/.ssh/authorized_keys` to enable public key authentication for the remainder of the deployment.

The `deploy.yml` file is intended to be self-documenting, so most of its contents should make sense: we have some DNS settings, some NTP settings, lists of IPs for our data nodes and the block devices on those nodes that will be provisioned, the Ansible-specific variables discussed above, and a list of IPs and netmasks from which management connections will be accepted.
