# Fixes to the default 3.9.0.0 reduced image.

# Build on object-reduced image (GA release)
FROM emcvipr/object:3.9.0.0-141228.b9e3c09a0d1-reduced

#Modified SS partition script for CE.
ADD storageserver-partition-config.sh /opt/storageos/bin/
RUN /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh
ADD rm /opt/storageos/bin/
RUN /usr/bin/chmod +x /opt/storageos/bin/rm
ADD eventsvc /opt/storageos/bin/
RUN /usr/bin/chmod +x /opt/storageos/bin/eventsvc
ADD storageos-dataservice /etc/init.d/storageos-dataservice
RUN /usr/bin/chmod +x /etc/init.d/storageos-dataservice
ADD shared-threadpool-conf.xml /opt/storageos/conf/shared-threadpool-conf.xml
# Allow allocation of different blocks of a chunk to be stored on the same partition for CE.
RUN f=/opt/storageos/conf/ssm-cf-conf.xml ; sed -i '200s/value="false"/value="true"/' $f
#UI removal of monitoring
ADD app.6fb9f5b2bd922a3cb087.js /opt/storageos/ecsportal/public/scripts/
