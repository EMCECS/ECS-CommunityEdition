#!/usr/bin/env bash

cd $HOME/ECS-CommunityEdition

./bootstrap.sh -y -b http://cache.local/alpine -g -o 192.168.2.2 -k contrib/sslproxycert/emc_ssl.pem -r cache.local:5000 -d examples/local-lab-3-node/registry.crt -p cache.local:3128 -t www.emc.com:443 -c docs/design/reference.deploy.yml
