# Fixes to the default 3.0 HF2 reduced image.
FROM emcvipr/object:3.0.0.0-86889.0a0ee19-reduced

# Increase memory for transformsvc
RUN sed -i s/-Xmx128m/-Xmx512m/ /opt/storageos/bin/transformsvc

# Fix disk partitioning script
RUN sed -i '/VMware/ s/$/ \&\& [ ! -e \/data\/is_community_edition ]/' /opt/storageos/bin/storageserver-partition-config.sh

# COPY vnest-common-conf-template.xml /opt/storageos/conf/vnest-common-conf-template.xml
RUN f=/opt/storageos/conf/vnest-common-conf-template.xml; grep -q "object.UseSeparateThreadPools" $f || sed -i '/properties id="serviceProperties"/a \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' $f

# Make vnest use separate thread pools to prevent deadlock
RUN printf "\n# Use separate thread pools to prevent deadlock in vnest init\nobject.UseSeparateThreadPools=true\n" >> /opt/storageos/conf/vnest.object.properties

