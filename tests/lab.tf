provider "vsphere" {
  user           = "${var.vsphere_user}"
  password       = "${var.vsphere_password}"
  vsphere_server = "${var.vsphere_server}"

  # if you have a self-signed cert
  allow_unverified_ssl = true
}

resource "vsphere_folder" "tests_folder" {
  path = "tests"
  datacenter = "${var.datacenter}"
}

resource "vsphere_virtual_machine" "install_node" {
  name   = "jenkins-ecsce-install"
  folder = "${vsphere_folder.tests_folder.path}"
  vcpu   = 2
  memory = 4096
  resource_pool = "${var.resource_pool}"
  datacenter    = "${var.datacenter}"
  skip_customization = true

  network_interface {
    label = "${var.network_interface}"
  }

  disk {
    template = "${var.template}"
    datastore = "${var.datastore}"
    type = "thin"
  }
}

resource "vsphere_virtual_machine" "ecs_node" {
  count  = "${var.ecs_nodes}"
  name   = "jenkins-ecsce-ecs-${count.index}"
  folder = "${vsphere_folder.tests_folder.path}"
  vcpu   = 4
  memory = 16384
  resource_pool = "${var.resource_pool}"
  datacenter    = "${var.datacenter}"
  skip_customization = true

  network_interface {
    label = "${var.network_interface}"
  }

  disk {
    template = "${var.template}"
    datastore = "${var.datastore}"
    type = "thin"
  }
}
