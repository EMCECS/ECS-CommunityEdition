provider "vsphere" {
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
  path               = "tests"
  type               = "vm"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
}

resource "vsphere_virtual_machine" "install_node" {
  name               = "jenkins-ecsce-install-${substr(sha1(timestamp()),0,8)}"
  folder             = "${vsphere_folder.tests_folder.path}"
  num_cpus           = 2
  memory             = 4096
  resource_pool_id   = "${data.vsphere_resource_pool.pool.id}"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
  guest_id           = "${data.vsphere_virtual_machine.template.guest_id}"
  scsi_type          = "${data.vsphere_virtual_machine.template.scsi_type}"

  network_interface {
    network_id       = "${data.vsphere_network.net.id}"
    adapter_type     = "${data.vsphere_virtual_machine.template.network_interface_types[0]}"
  }

  disk {
    name             = "jenkins-ecsce-install-disk-${substr(sha1(timestamp()),0,8)}"
    size             = "${data.vsphere_virtual_machine.template.disks.0.size}"
    eagerly_scrub    = "${data.vsphere_virtual_machine.template.disks.0.eagerly_scrub}"
    thin_provisioned = true
  }

  clone {
    template_uuid    = "${data.vsphere_virtual_machine.template.id}"
  }
}

resource "vsphere_virtual_machine" "ecs_node" {
  count              = "${var.ecs_nodes}"
  name               = "jenkins-ecsce-ecs-${count.index}-${substr(sha1(timestamp()),0,8)}"
  folder             = "${vsphere_folder.tests_folder.path}"
  num_cpus           = 4
  memory             = 16384
  resource_pool_id   = "${data.vsphere_resource_pool.pool.id}"
  datacenter_id      = "${data.vsphere_datacenter.dc.id}"
  guest_id           = "${data.vsphere_virtual_machine.template.guest_id}"
  scsi_type          = "${data.vsphere_virtual_machine.template.scsi_type}"

  network_interface {
    network_id       = "${data.vsphere_network.net.id}"
    adapter_type     = "${data.vsphere_virtual_machine.template.network_interface_types[0]}"
  }

  disk {
    name             = "jenkins-ecsce-install-disk-${substr(sha1(timestamp()),0,8)}"
    size             = "${data.vsphere_virtual_machine.template.disks.0.size}"
    eagerly_scrub    = "${data.vsphere_virtual_machine.template.disks.0.eagerly_scrub}"
    thin_provisioned = true
  }

  clone {
    template_uuid    = "${data.vsphere_virtual_machine.template.id}"
  }
}
