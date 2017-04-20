#!/usr/bin/env ash

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
