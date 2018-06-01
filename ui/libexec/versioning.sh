#!/usr/bin/env bash

context='local'

# TODO: Better develop test than detecting ci directory
if [ -d "ci" ]; then

    if [ -f "ci/ci_serial" ]; then
        serial="$(cat ci/ci_serial)"
        echo "$((++serial))" > "ci/ci_serial"
    else
        serial=0
        echo "$((++serial))" > "ci/ci_serial"
    fi

    ver_tag="dev.$(hostname -s).${serial}"
    context='develop'
    repo_name='padthaitofuhot'
    tag='develop'

elif [ -f "build/serial" ]; then

    serial="$(cat build/serial)"
    echo "$((++serial))" > build/serial
    ver_tag="${ver_tag}-${serial}"
    context='release'

elif [ -f local_serial ]; then

    serial="$(cat local_serial)"
    echo "$((++serial))" > local_serial
    ver_tag="local.$(hostname -s).${serial}"

else

    serial=0
    echo "$((++serial))" > local_serial
    ver_tag="local.$(hostname -s).${serial}"

fi

version="${ver_maj}.${ver_min}.${ver_rev}-${ver_tag}"

registry_flag=${registry_flag:-false}

if $registry_flag; then
    repo_path="${registry_val}/${repo_name}"
else
    repo_path="${repo_name}"
fi

full_image_path="${repo_path}/${image_name}:${version}"
untagged_image_path="${repo_path}/${image_name}"
latest_image_path="${repo_path}/${image_name}:${tag}"
dockerhub_image_path="${repo_name}/${image_name}:${version}"
