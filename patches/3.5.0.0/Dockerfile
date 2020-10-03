# Fixes to the default 3.5.0.0 reduced image.

# Build on object-reduced image (GA release)
FROM emcvipr/object:3.5.0.0-120520.8c29468ee8b-reduced

# Fix disk partitioning script
RUN sed -i '/VMware/ s/$/ \&\& [ ! -e \/data\/is_community_edition ]/' /opt/storageos/bin/storageserver-partition-config.sh \
    && /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh

# Set VNest useSeperateThreadPools to True
#RUN f=/opt/storageos/conf/vnest-common-conf.xml; grep -q "object.UseSeparateThreadPools" $f || sed -i '547i \ \ \ \ \ \ \ \ <prop key="object.UseSeparateThreadPools">true</prop>' $f

# Allow allocation of different blocks of a chunk to be stored on the same partition
#RUN f=/opt/storageos/conf/ssm-cf-conf.xml; grep -q '<config:boolean name="allowAllocationOnIgnoredPartitions" value="true" description="If set to true, different blocks in one chunk may be allocated on the same partition"/>' $f || sed -i 's#<config:boolean name="allowAllocationOnIgnoredPartitions" value="false" description="If set to true, different blocks in one chunk may be allocated on the same partition"/>#<config:boolean name="allowAllocationOnIgnoredPartitions" value="true" description="If set to true, different blocks in one chunk may be allocated on the same partition"/>#g' /opt/storageos/conf/ssm-cf-conf.xml $f

## Increase memory for transformsvc
#RUN sed -i s/Xmx128m/Xmx512m/ /opt/storageos/bin/transformsvc

## Set memory for objcontrolsvc
#RUN sed -i s/Xmx96m/Xmx256m/ /opt/storageos/bin/objcontrolsvc

# Set georeceiver's initialBufferNumOnHeap to something smaller for CE
#RUN f=/opt/storageos/conf/georeceiver-conf.xml; grep -q 'name="initialBufferNumOnHeap" value="5"' $f ||  sed -i 's/name="initialBufferNumOnHeap" value="60"/name="initialBufferNumOnHeap" value="5"/' $f
#RUN f=/opt/storageos/conf/georeceiver-conf.xml; grep -q '<prop key="object.InitialBufferNumOnHeap">10</prop>' $f || sed -i 's#<prop key="object.InitialBufferNumOnHeap">80</prop>#<prop key="object.InitialBufferNumOnHeap">10</prop>#g' $f

# Configure CM Object properties: Disable minimum storage device count
#RUN f=/opt/storageos/conf/cm.object.properties; grep -q 'MustHaveEnoughResources=false' $f ||  sed -i 's/MustHaveEnoughResources=true/MustHaveEnoughResources=false/' $f
