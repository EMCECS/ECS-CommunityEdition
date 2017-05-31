#!/usr/bin/env bash
# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

cd $HOME/ECS-CommunityEdition

./bootstrap.sh -y -g -r cache.local:5000 -d examples/local-lab-1-node/registry.crt -p cache.local:3128 -m cache.local -c examples/local-lab-aio/deploy.yml
