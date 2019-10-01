#!/usr/bin/env bash

# this script should be used to generate an overlay Dockerfile, which may be applied on top of an object container image, reducing various parameters.

if [ "$#" -lt 2 ]; then
	echo "Usage: $0 <object image> <dockerfile>"
	echo "Example: $0 emcvipr/object:3.2.0.0-101423.d3b297f-reduced /path/to/Dockerfile"
	exit 1
fi

obj_image=$1
df=$2

echo "$0 creating $df to build reduced image from $obj_image"

cat>$df<<EOF
FROM $obj_image
COPY patch_script.sh /opt/storageos/bin/patch_script.sh
RUN /bin/sh /opt/storageos/bin/patch_script.sh
EOF
