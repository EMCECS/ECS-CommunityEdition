#!/usr/bin/env bash

cd $HOME/ECS-CommunityEdition

./bootstrap.sh -y -v -b http://cache.local/alpine -g -o 192.168.2.2 -k contrib/sslproxycert/emc_ssl.pem -r cache.local:5000 -d examples/local-lab-1-node/registry.crt -p cache.local:3128 -c examples/local-lab-4-node/deploy.yml
