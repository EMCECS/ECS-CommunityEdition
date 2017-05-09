#!/usr/bin/env bash

cd $HOME/ECS-CommunityEdition

./bootstrap.sh -y -b http://cache.local/alpine -g -r cache.local:5000 -d examples/local-lab-1-node/registry.crt -p cache.local:3128 -c examples/local-lab-1-node/deploy.yml
