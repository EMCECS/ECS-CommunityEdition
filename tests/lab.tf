provider "vsphere" {
  version              = "~> 1.3.0"
  user                 = "${var.vsphere_user}"
  password             = "${var.vsphere_password}"
  vsphere_server       = "${var.vsphere_server}"
  # if you have a self-signed cert
  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name               = "${var.datacenter}"
}

data "vsphere_datastore" "ds" {
  name               = "${var.datastore}"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_resource_pool" "pool" {
  name               = "${var.resource_pool}"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_network" "net" {
  name               = "${var.network_interface}"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_virtual_machine" "template" {
  name               = "${var.template}"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
}

resource "vsphere_folder" "tests_folder" {
  path               = "ecsce-test-${substr(sha1(timestamp()),0,8)}"
  type               = "vm"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
}

resource "vsphere_virtual_machine" "install_node" {
  name               = "jenkins-ecsce-install"
  folder             = "${vsphere_folder.tests_folder.path}"
  num_cpus           = 2
  memory             = 4096
  resource_pool_id   = "${data.vsphere_resource_pool.pool.id}"
  datastore_id       = "${data.vsphere_datastore.ds.id}"
  guest_id           = "${data.vsphere_virtual_machine.template.guest_id}"
  scsi_type          = "${data.vsphere_virtual_machine.template.scsi_type}"

  network_interface {
    network_id       = "${data.vsphere_network.net.id}"
    adapter_type     = "${data.vsphere_virtual_machine.template.network_interface_types[0]}"
  }

  disk {
    label            = "jenkins-ecsce-install.vmdk"
    size             = "${data.vsphere_virtual_machine.template.disks.0.size}"
    thin_provisioned = true
    unit_number      = 0
  }

  disk {
    label            = "jenkins-ecsce-install_1.vmdk"
    size             = "${data.vsphere_virtual_machine.template.disks.1.size}"
    thin_provisioned = true
    unit_number      = 1
  }

  clone {
    template_uuid    = "${data.vsphere_virtual_machine.template.id}"
  }
}

resource "vsphere_virtual_machine" "ecs_node" {
  count              = "${var.ecs_nodes}"
  name               = "jenkins-ecsce-ecs-${count.index}"
  folder             = "${vsphere_folder.tests_folder.path}"
  num_cpus           = 4
  memory             = 16384
  resource_pool_id   = "${data.vsphere_resource_pool.pool.id}"
  datastore_id       = "${data.vsphere_datastore.ds.id}"
  guest_id           = "${data.vsphere_virtual_machine.template.guest_id}"
  scsi_type          = "${data.vsphere_virtual_machine.template.scsi_type}"

  network_interface {
    network_id       = "${data.vsphere_network.net.id}"
    adapter_type     = "${data.vsphere_virtual_machine.template.network_interface_types[0]}"
  }

  disk {
    label            = "jenkins-ecsce-ecs-${count.index}.vmdk"
    size             = "${data.vsphere_virtual_machine.template.disks.0.size}"
    thin_provisioned = true
    unit_number      = 0
  }

  disk {
    label            = "jenkins-ecsce-ecs-${count.index}_1.vmdk"
    size             = "${data.vsphere_virtual_machine.template.disks.1.size}"
    thin_provisioned = true
    unit_number      = 1
  }

  clone {
    template_uuid    = "${data.vsphere_virtual_machine.template.id}"

  }
}
