#!/usr/bin/env bash
sudo docker rmi --force $(sudo docker images | grep ecs-install | awk '{print $3}' | uniq)
