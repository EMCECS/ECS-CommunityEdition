#!/usr/bin/env bash

if [ -z "$*" ]; then
	echo "Usage: $0 <image directory>"
	echo "Example: $0 3.2.0.0"
	exit 1
fi

IMAGE_DIR=$1
IMAGE_CONF="${IMAGE_DIR}/image.conf"
if ! [ -f "${IMAGE_CONF}" ]; then
    echo "Unable to open ${IMAGE_CONF}"
    exit 1
fi

source "${IMAGE_CONF}"

bash libexec/gen_dockerfile.sh "${BASE_IMAGE}" "${IMAGE_DIR}/Dockerfile"
cp libexec/patch_script.sh "${IMAGE_DIR}"
cd "${IMAGE_DIR}"
docker build -t "${IMAGE_REPO}:${IMAGE_VERSION}" .
cd -
