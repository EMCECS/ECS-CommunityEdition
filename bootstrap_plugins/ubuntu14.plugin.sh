# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# packages to install before others
# Must install epel-release prior to pip.
list_prefix_packages='python-devel curl'
# command to run after installing prefix_packages
cmd_prefix_packages='curl -fsSL https://get.docker.com/ | sudo sh && sudo systemctl enable --now docker'
# packages to install
list_general_packages='git sqlite rsync'
# command to run after installing general_packages
cmd_general_packages=''
# packages to install after others
list_suffix_packages=''
# command to run after installing suffix_packages
cmd_suffix_packages=''
# packages to install if a VM
list_vm_packages='dkms qemu-guest-agent open-vm-tools'
# command to run after installing vm_packages
cmd_vm_packages=''
# command to install an os package manager package
cmd_in_repo_pkg='sudo apt-get -y install'
# command to update all packages in the os package manager
cmd_up_repo_all='sudo apt-get -y upgrade'
# command to enable a repo in the os package manager
cmd_enable_repo='sudo yum-config-manager --enable '
# command to rebuild the os package manager's database
cmd_up_repo_db='sudo apt-get -y update'
# command to set os package manager proxy
cmd_set_repo_proxy="echo 'proxy=http://${http_proxy}/' | sudo tee -a /etc/yum.conf"
# config script to fixup repos to properly use proxycaches
cmd_set_repo_conf="sudo sed -i -e 's/#baseurl=/baseurl=/' /etc/yum.repos.d/* && sudo sed -i -e 's/mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/*"
# command to set the proxy for the whole OS
cmd_set_os_proxy="echo -n http_proxy=${http_proxy}\nhttps_proxy=${http_proxy}\nftp_proxy=${http_proxy} | sudo tee -a /etc/environment"
# command to determine if the OS needs restarting after package updates
cmd_get_os_needs_restarting='sudo stat /var/run/reboot-required'
# command to reboot the system
cmd_do_reboot='sudo reboot'
# command to install a python PIP package
cmd_in_pip_pkg='sudo pip install --upgrade'
# command to download a python PIP package
cmd_get_pip_pkg='pip download'
