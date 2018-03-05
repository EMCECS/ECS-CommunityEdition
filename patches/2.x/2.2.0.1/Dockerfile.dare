# Two fixes to the default 2.2.0.0 image.
FROM emccorp/ecs-software-dare:2.2.0.1

ADD storageserver-partition-config.sh /opt/storageos/bin/
ADD storageos-ssm.jar /opt/storageos/lib/

# For vLab, disable transformsvc
ADD storageos-dataservice /etc/init.d/

# Make vnest use separate thread pools
RUN grep -l 'object.UseSeparateThreadPools' /opt/storageos/conf/*.object.properties | while read f; do sed -r -i "s/object.UseSeparateThreadPools\s*=\s*false/object.UseSeparateThreadPools=true/g" "$f"; done
