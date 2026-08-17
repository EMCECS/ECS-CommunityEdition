FROM emcvipr/object:4.4.0.0-143516.a68cbda81306-reduced

USER root

ADD --chmod=0755 storageserver-partition-config.sh /opt/storageos/bin/
ADD --chmod=0755 storageos-dataservice /etc/init.d/storageos-dataservice
ADD shared-threadpool-conf.xml /opt/storageos/conf/shared-threadpool-conf.xml

RUN f=/opt/storageos/conf/ssm-cf-conf.xml ; \
    sed -i 's#name="allowAllocationOnIgnoredPartitions" value="false"#name="allowAllocationOnIgnoredPartitions" value="true"#g' $f && \
    grep -q 'name="allowAllocationOnIgnoredPartitions" value="true"' $f

RUN f=/opt/storageos/conf/shared-cf-conf.xml ; \
    sed -i 's#name="geo_communication_protocol" value="https"#name="geo_communication_protocol" value="http"#g' $f && \
    grep -q 'name="geo_communication_protocol" value="http"' $f && \
    sed -i 's#<config:boolean name="ssl" value="true"#<config:boolean name="ssl" value="false"#g' $f && \
    grep -q '<config:boolean name="ssl" value="false"' $f

USER storageos
