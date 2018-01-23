variable "vsphere_user" {}
variable "vsphere_password" {}
variable "vsphere_server" {}
variable "datastore" {}
variable "template" {}
variable "resource_pool" {}
variable "datacenter" {}
variable "network_interface" {}
variable "ecs_nodes" {}
variable "timestamp" {
  default = "${substr(sha1(timestamp()),0,8)}"
}
