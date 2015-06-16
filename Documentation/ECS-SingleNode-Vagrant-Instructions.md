# ECS SW 2.0 Single Node Vagrant Deployment

**Table of Contents**

- [Requirements](#requirements)
- [Using Vagrant](#using-vagrant)
  - [Troubleshooting](#troubleshooting)


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


## Using Vagrant

You can use Vagrant to prepare a remote machine with SSH access. You will just need to configure the SSH credentials and Vagrant will take care of installing the ECS in the single node mode.

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

Now, let's link it to the remote host by running `vagrant up`. To check that we can connect, we will run `vagrant ssh`. If everything goes right, you will access the remote host. You can now exit from there and run `vagrant provision` to prepare the remote host and install ECS in single node mode.


### Troubleshooting

You may see the following errors while running `vagrant provision`.

    sudo: sorry, you must have a tty to run sudo

To solve this, you will need to edit the sudoers file and the tty when running sudo. Log in to the remote machine and edit the `/etc/sudoers`

    sudo vi /etc/sudoers

Look for the line that contains `Defaults   requiretty` and comment it.

    #Defaults requiretty


Now, you may also see the following error.

    sudo: no tty present and no askpass program specified


Login to the remote machine and run.

    sudo visudo

Then, add the following lines at the end of the file.

    username     ALL=(ALL) NOPASSWD: ALL
    username     ALL=(ALL:ALL) NOPASSWD: ALL

Replace `username` by the user that is actually logging in via SSH.
