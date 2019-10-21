# Fixes to the default 3.3.0.1 reduced image.

# Build on object-reduced image (GA release)
FROM emccorp/ecs-software-3.3.0:3.3.0.1

# Fix disk partitioning script
RUN sed -i '/VMware/ s/$/ \&\& [ ! -e \/data\/is_community_edition ]/' /opt/storageos/bin/storageserver-partition-config.sh \
    && /usr/bin/chmod +x /opt/storageos/bin/storageserver-partition-config.sh

