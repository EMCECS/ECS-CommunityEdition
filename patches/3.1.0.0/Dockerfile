# Fixes to the default 3.1.0.0 reduced image.
# RC4
FROM emcvipr/object:3.1.0.0-95266.ab2753a-reduced

# Increase memory for transformsvc
RUN sed -i s/-Xmx128m/-Xmx512m/ /opt/storageos/bin/transformsvc

# Fix disk partitioning script
RUN sed -i '/VMware/ s/$/ \&\& [ ! -e \/data\/is_community_edition ]/' /opt/storageos/bin/storageserver-partition-config.sh

RUN /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh

# Make vnest use separate thread pools to prevent deadlock
RUN printf "\n# Use separate thread pools to prevent deadlock in vnest init\nobject.UseSeparateThreadPools=true\n" >> /opt/storageos/conf/vnest.object.properties

RUN f=/opt/storageos/conf/vnest-common-conf-template.xml; grep -q "object.UseSeparateThreadPools" $f || sed -i '/properties id="serviceProperties"/a \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' $f
