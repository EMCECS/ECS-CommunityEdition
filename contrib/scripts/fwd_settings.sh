#!/bin/bash

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# Updates FirewallD settings with trusted ports in accordance with ECS requirements.

tcpadd=( 2 25 111 80 389 443 636 1095 1096 1098 1198 1298 2049 2181 2889 3218 4443 5120 5123 7399 7400 7578 9010 9011 9020-9025 9028 9029 9040 9069 9091 9094-9101 9111 9201-9206 9208 9209 9212 9230 9250 9888 9898 )
udpadd=( 1095 1096 1098 1198 1298 3218 9091 9094 9100 9201 9203 9208 9209 9250 9888 )

systemctl enable firewalld
systemctl start firewalld

for port in "${tcpadd[@]}"; do
    firewall-cmd --permanent --add-port=$port/tcp
done
for port in "${udpadd[@]}"; do
    firewall-cmd --permanent --add-port=$port/udp
done

firewall-cmd --reload
exit 0
