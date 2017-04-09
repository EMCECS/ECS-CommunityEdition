#!/usr/bin/env bash

cd $HOME/ECS-CommunityEdition

./bootstrap.sh -y -b http://cache.gotham.local/alpine -g -k contrib/sslproxycert/emc_ssl.pem -r cache.gotham.local:5000 -d examples/vmware-lab-4-node/registry.crt -p cache.gotham.local:3128 -c examples/vmware-lab-4-node/lab.yml
