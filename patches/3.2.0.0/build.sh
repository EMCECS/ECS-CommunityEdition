#!/usr/bin/env bash
IMAGE_REPO="emccorp/ecs-software-3.2.0"
IMAGE_VERSION="3.2.0.0"

docker build -t "${IMAGE_REPO}:${IMAGE_VERSION}" .
