#!/usr/bin/env bash


# Helpers for spammy sections
img_build_fail() {
    error "Failed to build the installer image. Check the log for details."
    die "You may need to run '$0 --clean' to clean up Docker"
}

img_pull_fail() {
    die "Failed to pull the installer image. Check the log for details."
    die "You may need to run '$0 --clean' to clean up Docker"
}

ui_tarball() {
    TEMPTAR=$(mktemp /tmp/tmp.XXXXXXXX)
    cd "${root}"
    tar -czf "${TEMPTAR}" . || return 1
    cd "${root}"
    mv -f "${TEMPTAR}" "ui/resources/docker/ecs-install.${version}.tgz" || return 1
    echo "ui/resources/docker/ecs-install.${version}.tgz"
}

fetch() {
    cd /tmp
    filename="$(curl -fsSLOw '%{filename_effective}\n' ${1} || img_build_fail)"
    cd "${root}"
    mv -f "/tmp/${filename}" "ui/resources/docker/${filename}"
    echo "ui/resources/docker/${filename}"
    return 0
}

git_tarball() {

    git_name="${1}"
    git_url="${2}"
    git_branch="${3}"
    git_massage="${4}"
    TEMPGIT=$(mktemp /tmp/tmp.XXXXXXXX)

    if $proxy_flag; then
        git config --global http.proxy "${proxy_val}"
    fi

    cd /tmp

    if ! [ -d "${git_name}" ]; then
        git clone -q "${git_url}"
        cd "${git_name}"
        [ -f .gitmodules ] && git submodule -q update --init --recursive
        git checkout -q "${git_branch}"
        [ -f .gitmodules ] && git submodule -q update --recursive
        ! [ -z "${git_massage}" ] && $git_massage "/tmp/${git_name}"
        cd /tmp
    fi

    tar -czf "${TEMPGIT}" --exclude='.git' "${git_name}"
    cd "${root}"
    mv -f "${TEMPGIT}" "ui/resources/docker/${git_name}-git-${git_branch}.tgz"
    echo "ui/resources/docker/${git_name}-git-${git_branch}.tgz"
}

venv() {
    cd "${*}"
    virtualenv -q .
    source bin/activate
    pip install -q -e .
    virtualenv -q --relocatable .
    # W/A for broken BitTornado setup
    [ -d icons ] && mv icons bin/
    deactivate
}

docker_test() {
    docker_hello=$(sudo docker run --rm ${hello_image} 2>&1)
    if [ -z "${docker_test##*'Hello from Docker'*}" ]; then
        return 0
    else
        return 1
    fi
}

docker_registry() {
    if $registry_flag; then
        hello_image="${registry_val}/hello-world"
        if $regcert_flag; then
            set_docker_reg_cert "${registry_val}" "${regcert_val}" 2>&1 | log
            if ! [ -d /opt/emc/ssl ]; then
                sudo mkdir -p "${docker_host_root}/ssl"
            fi
            sudo cp "${regcert_val}" "${docker_host_root}/ssl/docker.pem"
        fi
    else
        hello_image="hello-world"
    fi
}

docker_clean() {
    o "Cleaning up... "

    o "     [build tmp containers] "
    if ! [ -z "$(sudo docker ps -a | grep ecs-install_tmp)" ]; then
        sudo docker rm -vf ecs-install_tmp >/dev/null
    fi

    o "     [ecs-install data containers] "
    if ! [ -z "$(sudo docker ps -a | grep ecs-install-data)" ]; then
        sudo docker rm -vf ecs-install-data >/dev/null
    fi

    o "     [exited containers] "
    if ! [ -z "$(sudo docker ps -q -f status=exited)" ]; then
        sudo docker rm -vf $(sudo docker ps -q -f status=exited | grep -v ecs-config) >/dev/null
    fi

    o "     [dangling layers] "
    if ! [ -z "$(sudo docker images -q --filter "dangling=true")" ]; then
        sudo docker rmi $(sudo docker images -q --filter "dangling=true") >/dev/null
    fi
}

docker_set_artifact() {
### ECS Docker Image
    o "Pulling ${release_artifact}:${release_tag} Docker image"
    if $registry_flag; then
        if ! sudo docker pull ${registry_val}/${release_artifact}:${release_tag}; then
            error "We couldn't pull the software image for some reason. Since you're using a custom"
            error "registry, it may be that the image does not exist in your registry. Please ensure"
            error "the '${release_artifact}' image is present on your registry before trying again, or"
            error "perhaps you can simply pull the image directly from DockerHub."
            die "If you still need more help after trying the above, you can reach us on GitHub."
            # This has to be tagged for the cache generator in Ansible
        fi
        o "Tagging ${registry_val}/${release_artifact}:${release_tag} -> ${release_common_name}"
        sudo docker tag "${registry_val}/${release_artifact}:${release_tag}" "${release_common_name}"
    else
        if ! sudo docker pull "${release_artifact}:${release_tag}"; then
            error "We couldn't pull the software image for some reason. It may be a temporary issue"
            error "or there may be an issue with your Internet access. You'll likely need to check"
            error "the error message from the Docker pull output (above) to see what's specifically"
            error "the problem."
            die "If you still need more help after trying the above, you can reach us on GitHub."
        fi
        o "Tagging ${release_artifact}:${release_tag} -> ${release_common_name}"
        sudo docker tag "${release_artifact}:${release_tag}" "${release_common_name}"
    fi
}

data_container_missing() {
    [ -z "$(sudo docker ps -a | grep ecs-install-data)" ]
}

remove_data_container() {
    if ! [ -z "$(sudo docker ps -a | grep ecs-install-data)" ]; then
        sudo docker rm -vf ecs-install-data >/dev/null
    fi
}

make_new_data_container() {
    sudo docker run -d --name "${data_container_name}" \
        --entrypoint /bin/echo ${image_release} \
        echo "Data container for ecs-install" >/dev/null
}

collect_artifacts() {

    rm -f ${root}/ui/resources/docker/*.tgz

    case $context in

        local)
            ui_artifact="$(ui_tarball)" || img_build_fail
            #ansible_artifact="$(git_tarball ansible ${ansible_git_url} ${ansible_git_target})" || img_build_fail
        ;;
        release)
            ui_artifact="$(ui_tarball)" || img_build_fail
            #ansible_artifact="$(git_tarball ansible ${ansible_git_url} ${ansible_git_target})" || img_build_fail
        ;;
        develop)
            ui_artifact="$(ui_tarball)" || img_build_fail
            #ansible_artifact="$(git_tarball ansible ${ansible_git_url} ${ansible_git_target})" || img_build_fail
        ;;

    esac
}

create_apk_repositories() {
echo "${alpine_mirror}" | awk -v v="/${alpine_version}" '
    {
        print $1 v "/main"
        print $1 v "/community"
        print "@edge_main " $1 "/edge/main"
        print "@edge_community " $1 "/edge/community"
        print "@edge_testing " $1 "/edge/testing"
    }
' > "${root}/ui/resources/docker/apk-repositories"
}

docker_login() {
    while [ -z "$(sudo jq -r '.auths[].auth' ~root/.docker/config.json)" ]; do
        while ! sudo docker login; do
            echo "Please try again or CTRL-C to quit."
        done
    done
    return 0
}
