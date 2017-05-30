variable "vsphere_user" {}
variable "vsphere_password" {}
variable "vsphere_server" {}
variable "datastore" {
  default = "iSCSI-2"
}
variable "template" {
  default = "jenkins/ecsce-template"
}
variable "resource_pool" {
  default = "Cisco UCS Cluster/Resources/Tests"
}
variable "datacenter" {
  default = "Datacenter"
}
variable "network_interface" {
  default = "VM Network"
}
variable "ecs_nodes" {
  default = 1
}
