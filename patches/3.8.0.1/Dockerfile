# Fixes to the default 3.8.0.1 reduced image.

# Build on object-reduced image (GA release)
FROM emcvipr/object:3.8.0.1-138598.3d5db7c96f2-reduced

#Modified SS partition script for CE.
ADD storageserver-partition-config.sh /opt/storageos/bin/
RUN /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh

# Modify the SS partition script for CE.
RUN sed -i '/VMware/ s/$/ \&\& [ ! -e \/data\/is_community_edition ]/' /opt/storageos/bin/storageserver-partition-config.sh \
    && /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh

# Allow allocation of different blocks of a chunk to be stored on the same partition for CE.
RUN f=/opt/storageos/conf/ssm-cf-conf.xml ; sed -i '187s/value="false"/value="true"/' $f

#Modified dashboard for ECS CE.

ADD app.d4e76e5fa6bc1dc79cf5.js /opt/storageos/ecsportal/public/scripts/
