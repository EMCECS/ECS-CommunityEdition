#!/usr/bin/env bash
IMAGE_REPO="emccorp/ecs-software-3.1.0"
IMAGE_VERSION="3.1.0.3"

docker build -t "${IMAGE_REPO}:${IMAGE_VERSION}" .
