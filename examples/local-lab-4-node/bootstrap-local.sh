#!/usr/bin/env bash

cd $HOME/ECS-CommunityEdition

./bootstrap.sh -y -v -b http://cache.local/alpine -g -o 192.168.2.2 -k contrib/sslproxycert/emc_ssl.pem -r cache.local:5000 -d examples/local-lab-4-node/registry.crt -p cache.local:3128 -t www.emc.com:443 -c examples/local-lab-4-node/local-lab.yml
