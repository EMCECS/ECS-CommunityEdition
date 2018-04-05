output "install_node_ip" {
  value = "${vsphere_virtual_machine.install_node.default_ip_address}"
}

output "ecs_node_ip" {
  value = "${vsphere_virtual_machine.ecs_node.*.default_ip_address}"
}
