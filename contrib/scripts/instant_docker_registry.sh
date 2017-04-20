#!/usr/bin/env bash

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

###
# Run it on your soon-to-be docker registry host for great success.
###

if [ $UID != 0 ]; then
    echo "You need to be root for this to work."
    exit 1
fi

# Your SSL Certificate's common name (The name your host is known by,
# typically an FQDN).
FQDN=$(hostname -f)

# Flag to restart docker
FLAG_RESTART=false

# This is the minimum registry version supporting _catalog in the v2 API.
REGISTRY_VERSION="2"

echo "Creating paths"
for dir in certs store; do
    if ! [ -d /opt/registry/${dir} ]; then
        mkdir -p /opt/registry/${dir}
        FLAG_RESTART=true
    else
        echo "Reusing existing /opt/registry/${dir}"
    fi
done

if ! [ -f /opt/registry/certs/domain.key ] && ! [ -f /opt/registry/certs/domain.crt ]; then
    openssl req -newkey rsa:4096 -nodes -sha256 \
        -keyout /opt/registry/certs/domain.key -x509 \
        -days 9999 -out /opt/registry/certs/domain.crt \
        -subj "/C=AQ/ST=local/L=local/O=local/OU=local/CN=${FQDN}"
    FLAG_RESTART=true
else
    echo "Reusing existing /opt/registry/certs/domain.crt"
fi

if ! [ -d "/etc/docker/certs.d/${FQDN}:5000" ]; then
    mkdir -p "/etc/docker/certs.d/${FQDN}:5000"
    cp /opt/registry/certs/domain.crt \
        "/etc/docker/certs.d/${FQDN}:5000/ca.crt"
    FLAG_RESTART=true
else
    echo "Reusing existing /etc/docker/certs.d/${FQDN}:5000/ca.crt"
fi

# "The nice thing about standards is that you have so many to choose from;
# furthermore, if you do not like any of them, you can just wait
# for next year's model." -- -Andrew S. Tanenbaum
if $FLAG_RESTART; then
    systemctl daemon-reload || true
    systemctl restart docker || restart docker || service docker restart
    systemctl status docker || status docker || service docker status
    sleep 5
fi

docker run \
    -d \
    -p 5000:5000 \
    --restart=always \
    --name registry \
    -v /opt/registry/certs:/certs \
    -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
    -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
    -v /opt/registry/store:/var/lib/registry \
    registry:${REGISTRY_VERSION}

docker pull hello-world:latest
docker tag hello-world:latest ${FQDN}:5000/test/hello-world:test
docker push ${FQDN}:5000/test/hello-world:test
sleep 5
curl --cacert /opt/registry/certs/domain.crt https://${FQDN}:5000/v2/_catalog
