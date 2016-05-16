#!/bin/bash
# Updates FirewallD settings with trusted ports in accordance with ECS requirements.

tcpadd=( 80 389 443 636 1095 1096 1098 1198 1298 3218 4443 5120 5123 7578 9010 9011 9020-9025 9028 9029 9040 9069 9091 9094-9101 9111 9201-9206 9208 9209 9250 9888 9898 )
udpadd=( 1095 1096 1098 1198 1298 3218 9091 9094 9100 9201 9203 9208 9209 9250 9888 )

systemctl enable firewalld
systemctl start firewalld

for port in "${tcpadd[@]}"; do
    firewall-cmd --permanent --add-port=$port/tcp
for port in "&{udpadd[@]}"; do
    firewall-cmd --permanent --add-port=$port/udp

firewall-cmd --reload

done
exit 0
