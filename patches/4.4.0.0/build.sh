#!/usr/bin/env bash
source image.conf

docker build -t "${IMAGE_REPO}:${IMAGE_VERSION}" .
