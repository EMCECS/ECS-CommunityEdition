# Fixes to the default 3.0HF image.
FROM emcvipr/object:3.0.0.0-86239.1c9e5ec-reduced

# Increase memory for transformsvc
ADD transformsvc /opt/storageos/bin/

# Fix disk partitioning script
ADD storageserver-partition-config.sh /opt/storageos/bin/
RUN /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh

# Make vnest use separate thread pools to prevent deadlock
ADD vnest.object.properties /opt/storageos/conf/

RUN f=/opt/storageos/conf/vnest-common-conf-template.xml; grep -q "object.UseSeparateThreadPools" $f || sed -i '/properties id="serviceProperties"/a \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' $f
