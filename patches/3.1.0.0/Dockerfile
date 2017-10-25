# Fixes to the default 3.1.0.0 reduced image.
# RC4
FROM emcvipr/object:3.1.0.0-95266.ab2753a-reduced

# Increase memory for transformsvc
RUN sed -i s/-Xmx128m/-Xmx512m/ /opt/storageos/bin/transformsvc

# Fix disk partitioning script
RUN sed -i '/VMware/ s/$/ \&\& [ ! -e \/data\/is_community_edition ]/' /opt/storageos/bin/storageserver-partition-config.sh

RUN /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh

RUN f=/opt/storageos/conf/vnest-common-conf-template.xml; grep -q "object.UseSeparateThreadPools" $f || sed -i '/properties id="serviceProperties"/a \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' $f

# Set georeceiver's initialBufferNumOnHeap to something smaller for CE
RUN f=/opt/storageos/conf/georeceiver-conf.xml; grep -q 'name="initialBufferNumOnHeap" value="10"' $f ||  sed -i 's/name="initialBufferNumOnHeap" value="60"/name="initialBufferNumOnHeap" value="10"/' $f
