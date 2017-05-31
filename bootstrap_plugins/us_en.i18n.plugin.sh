#!/usr/bin/env bash
# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

error_building_ecs_install_image() {
    error "We couldn't build the ecs-install image for some reason. Please check the logs."
    error "If it's something simple, such as a missing base image (we use python:2.7-alpine),"
    error "then you may be able to get the image to build by pulling python:2.7-alpine from"
    error "a reliable source, such as DockerHub. If you specified a custom registry, then you"
    error "may need to first push the image into your registry to ensure it is available for"
    error "the build tool."
    die "If you still need more help after trying the above, you can reach us on github."
}
error_pulling_ecs_install_image() {
    error "We couldn't pull the ecs-install image for some reason. Please check the logs."
    error "If it's something simple, such as the ecs-install:latest image missing from"
    error "your custom Docker registry, or if your Internet access isn't working, then"
    error "you may be able to solve the problem by first solving one of the above issues."
    die "If you still need more help after trying the above, you can reach us on github."
}
error_pulling_ecs_software_image_from_registry() {
    error "We couldn't pull the software image for some reason. Since you're using a custom"
    error "registry, it may be that the image does not exist in your registry. Please ensure"
    error "the '${release_artifact}' image is present on your registry before trying again, or"
    error "perhaps you can simply pull the image directly from DockerHub."
    die "If you still need more help after trying the above, you can reach us on github."
}
error_pulling_ecs_software_image_from_dockerhub() {
    error "We couldn't pull the software image for some reason. It may be a temporary issue"
    error "or there may be an issue with your Internet access. You'll likely need to check"
    error "the error message from the Docker pull output (above) to see what's specifically"
    error "the problem."
    die "If you still need more help after trying the above, you can reach us on github."
}
