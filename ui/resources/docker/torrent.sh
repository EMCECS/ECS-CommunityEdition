#!/usr/bin/env ash
# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

# Start torrent tracker and seeder
torrent() {
    if [ -f /opt/ffx.sem ]; then
        opentracker -i 0.0.0.0 -p 6881 -d /var/run/opentracker -u nobody &
        cd /var/cache/emc
        aria2c -q -l /var/log/torrent.log -T /var/cache/emc/ecs-install/cache.torrent --seed-ratio=0.0 \
               --dht-listen-port=6882 --allow-overwrite=true --check-integrity \
               --listen-port=6883-6999 --enable-mmap=true 1>/dev/null 2>/dev/null &
        cd /
    fi
}

torrent
