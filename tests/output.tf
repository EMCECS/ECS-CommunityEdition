output "install_node_ip" {
  value = "${vsphere_virtual_machine.install_node.network_interface.0.ipv4_address}"
}

output "ecs_node_ip" {
  value = "${vsphere_virtual_machine.ecs_node.network_interface.0.ipv4_address}"
}
