# Fixes to the default 4.1.0.0 reduced image.

# Build on object-reduced image (GA release)
FROM emcvipr/object:4.2.0.0-142739.6747b7efd73c-reduced

#Modified SS partition script for CE.
ADD storageserver-partition-config.sh /opt/storageos/bin/
RUN /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh
#ADD rm /opt/storageos/bin/
#RUN /usr/bin/chmod +x /opt/storageos/bin/rm
#ADD eventsvc /opt/storageos/bin/
#RUN /usr/bin/chmod +x /opt/storageos/bin/eventsvc
ADD storageos-dataservice /etc/init.d/storageos-dataservice
RUN /usr/bin/chmod +x /etc/init.d/storageos-dataservice
ADD shared-threadpool-conf.xml /opt/storageos/conf/shared-threadpool-conf.xml
# Allow allocation of different blocks of a chunk to be stored on the same partition for CE.
RUN f=/opt/storageos/conf/ssm-cf-conf.xml ; sed -i '202s/value="false"/value="true"/' $f
#UI removal of monitoring
ADD app.1d17d2c66990816fc673.js /opt/storageos/ecsportal/public/scripts/
