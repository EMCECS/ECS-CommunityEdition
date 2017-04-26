#!/bin/ash

prefix="/usr/local/src"
init_container=false

source /etc/auto.conf

/usr/sbin/update-ca-certificates 1>/dev/null 2>/dev/null

unpack() {
    package="${1}"
    echo "Unpacking $(basename ${package} .tgz)"
    if [ -f "${prefix}/${package}" ]; then

        # Work in src dir
        cd "${prefix}"

        # Remove previous copy
        if [ -d "${prefix}/$(basename ${package} .tgz)" ]; then
            rm -rf "${prefix}/$(basename ${package} .tgz)"
        fi

        # Process package metadata if it exists
        if [ -f "${prefix}/$(basename ${package} .tgz).meta" ]; then

            source "${prefix}/$(basename ${package} .tgz).meta"

            if ! [ -z "${hash_cmd}" ]; then
                if ! "${hash_cmd}"; then
                    echo "${package} failed file checksum test"
                    return 1
                fi
                unset hash_cmd
            fi

            if ! [ -z "${unpack_cmd}" ]; then
                if ! "${unpack_cmd}"; then
                    echo "${package} failed to unpack"
                    return 1
                fi
                unset unpack_cmd
            else
                tar -xzf "${package}"
            fi

            if ! [ -z "${build_dir}" ]; then
                if ! cd "${prefix}/${build_dir}"; then
                    echo "${package} failed, could not cd to ${build_dir}"
                    return 1
                fi
                unset build_dir
            else
                cd "${prefix}/$(basename ${package} .tgz)"
            fi

            if ! [ -z "${build_cmd}" ]; then
                if ! "${build_cmd}" >/dev/null; then
                    echo "${package} failed to build."
                    return 1
                fi
                unset build_cmd
            else
                pip install -e .
            fi

        # Otherwise install normally
        else
            cd "${prefix}"
            if ! tar -xzf "${package}"; then
                echo "${package} failed to unpack"
                return 1
            fi
            if ! cd "${prefix}/$(basename ${package} .tgz)"*; then
                echo "${package} failed, could not cd to $(basename ${package} .tgz)"
                return 1
            fi
            if ! python setup.py build && python setup.py install; then
                echo "${package} failed to build."
                return 1
            fi
        fi
    else
        echo "Couldn't install ${package}, is the image built correctly?"
        return 1
    fi
}

if ! [ -x /usr/local/bin/ansible ] || ! [ -x /usr/local/bin/ ]; then
    echo "Initializing new data container"
    init_container=true
elif [ -f /etc/update.sem ]; then
    echo "Installing updates"
    rm -f /etc/update.sem
    init_container=true
fi

if $init_container; then
    unpack ansible.tgz
    unpack ui.tgz
    ecsdeploy init
fi

if ! [ -z "$*" ]; then
    $@
#elif [ -x /usr/local/bin/menu ]; then
#    menu
else
    /bin/ash -l
fi
