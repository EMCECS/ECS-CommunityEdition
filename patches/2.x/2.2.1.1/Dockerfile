# Fixes to the default 2.2.1.0 image.
FROM emcvipr/object:2.2.1.0-77706.493e577-reduced

# Reduce timeout for systems that are shutdown for a while
ADD coordinator.properties /opt/storageos/conf/
# Increase memory for transformsvc 
ADD transformsvc /opt/storageos/bin/

# Fix disk partitioning script
ADD storageserver-partition-config.sh /opt/storageos/bin/

# Make vnest use separate thread pools to prevent deadlock
#ADD vnest.object.properties /opt/storageos/conf/
RUN f=/opt/storageos/conf/vnest-common-conf-template.xml; grep -q "object.UseSeparateThreadPools" $f || sed -i '/properties id="serviceProperties"/a \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' $f

# Increase memory for transformsvc
ADD transformsvc /opt/storageos/bin/
# Patch for small disk footprint disk allocation
ADD storageos-ssm.jar /opt/storageos/lib/

# Remove forced exit from systool
ADD systool /etc/
