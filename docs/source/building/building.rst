Building ``ecs-install`` Image From Sources
===========================================

The ECS-CommunityEdition git repository is also a build environment for
the ``ecs-install`` image.

Building ``ecs-install`` Image During Bootstrap with ``boostrap.sh``
--------------------------------------------------------------------

If you're hacking around in the install node code, then you'll probably
want to build your own install node image at some point. The
``bootstrap.sh`` script has options for accomplishing just this.

::

    [Usage]
     -h, --help
        Display this help text and exit
     --help-build
        Display build environment help and exit
     --version
        Display version information and exit

    [Build Options]
     --zero-fill-ova
        Reduce ephemera, defrag, and zerofill the instance after bootstrapping
     --build-from <URL>
        Use the Alpine Linux mirror at <URL> to build the ecs-install image locally.
        Mirror list: https://wiki.alpinelinux.org/wiki/Alpine_Linux:Mirrors

All you'll need is a URL that points to an Alpine Linux mirror. For a
good default, you can use the GeoDB enabled CDN mirror, which should
auto-select a nearby mirror for you based on your public edge IP:
http://dl-cdn.alpinelinux.org/alpine/

To tell bootstrap to build the image for you, just include the
``--build-from`` argument on your command line, like so:

``[admin@localhost ECS-CommunityEdition]$ ./bootstrap.sh --build-from http://dl-cdn.alpinelinux.org/alpine/``

Building ``ecs-install`` Image After Bootstrapping with ``build_image``
-----------------------------------------------------------------------

If you need to build the ``ecs-install`` image after bootstrapping, then
you'll need to give a valid Alpine Linux mirror to your install node:

::

    [admin@installer-230 ECS-CommunityEdition]$ build_image --update-mirror http://cache.local/alpine/
    > Updating bootstrap.conf to use Alpine Linux mirror http://cache.local/alpine/

Once the mirror is configured, you can then build the image:

::

    [admin@installer-230 ECS-CommunityEdition]$ build_image
    > Building image ecs-install
    > Build context is: local
    > Using custom registry: cache.local:5000
    > Tunneling through proxy: cache.local:3128
    > Checking Alpine Linux mirror
    > Generating Alpine Linux repositories file
    > Collecting artifacts
    > UI artifact is: ui/resources/docker/ecs-install.2.5.1-local.installer-230.4.tgz
    INFO[0000] FROM cache.local:5000/alpine:3.6
    INFO[0000] | Image sha256:37eec                          size=3.962 MB
    INFO[0000] LABEL MAINTAINER='Travis Wichert <travis.wichert@emc.com>'
    INFO[0000] ENV ANSIBLE_CONFIG="/etc/ansible/ansible.cfg"
    INFO[0000] ENV ANSIBLE_HOSTS="/usr/local/src/ui/inventory.py"
    INFO[0000] Commit changes
    INFO[0000] | Cached! Take image sha256:302bc    size=3.962 MB (+0 B)
    INFO[0000] COPY ui/resources/docker/ecs-install-requirements.txt /etc/ecs-install-requirements.txt
    INFO[0000] | Calculating tarsum for 1 files (465 B total)
    INFO[0000] | Cached! Take image sha256:44a83    size=3.962 MB (+465 B)
    INFO[0000] COPY ui/resources/docker/apk-repositories /etc/apk/repositories
    INFO[0000] | Calculating tarsum for 1 files (239 B total)
    INFO[0000] | Not cached
    INFO[0000] | Created container 89e5a010f1b5 (image sha256:44a83)
    INFO[0000] | Uploading files to container 89e5a010f1b5
    INFO[0000] Commit changes
    INFO[0001] | Result image is sha256:26c0f                size=3.962 MB (+239 B)
    INFO[0001] | Removing container 89e5a010f1b5
    INFO[0001] ENV http_proxy=http://cache.local:3128
    INFO[0001] ENV pip_proxy=cache.local:3128
    INFO[0001] Commit changes
    INFO[0002] | Created container 49b210eacd7c (image sha256:26c0f)
    INFO[0002] | Result image is sha256:d9d58                size=3.962 MB (+0 B)
    INFO[0002] | Removing container 49b210eacd7c
    INFO[0003] RUN apk -q update &&     apk -q --no-cache upgrade
    INFO[0003] | Created container 856a966289a6 (image sha256:d9d58)
    INFO[0005] Commit changes
    INFO[0006] | Result image is sha256:a2978                size=6.855 MB (+2.893 MB)
    INFO[0006] | Removing container 856a966289a6
    INFO[0006] RUN apk -q --no-cache add python2 py-pip                             openssh-client sshpass openssl ca-certificates libffi libressl@edge_main                              pigz jq less                              opentracker aria2 mktorrent@edge_community                              ansible@edge_main
    INFO[0006] | Created container 2c940cb6c2e6 (image sha256:a2978)
    INFO[0016] Commit changes
    INFO[0026] | Result image is sha256:b806e                size=124.4 MB (+117.6 MB)
    INFO[0026] | Removing container 2c940cb6c2e6
    INFO[0026] RUN mv /etc/profile.d/color_prompt /etc/profile.d/color_prompt.sh     && ln -s /usr/local/src/ui/ansible /ansible     && ln -s /usr/local/src/ui /ui     && ln -s /usr/local/src /src     && ln -s /usr/bin/python /usr/local/bin/python     && mkdir -p /var/run/opentracker     && chown nobody:nobody /var/run/opentracker
    INFO[0027] | Created container a5a35a59e61a (image sha256:b806e)
    INFO[0027] Commit changes
    INFO[0029] | Result image is sha256:55ae2                size=124.4 MB (+295 B)
    INFO[0029] | Removing container a5a35a59e61a
    INFO[0029] RUN apk -q --no-cache add --update --virtual .build-deps musl-dev python2-dev libffi-dev                        build-base make openssl-dev linux-headers git gcc git-perl     && if ! [ -z "$pip_proxy" ]; then             export pip_proxy="--proxy $pip_proxy" &&             git config --global http.proxy "$http_proxy"        ;fi     && pip install -q $pip_proxy --no-cache-dir -r /etc/ecs-install-requirements.txt     && apk -q --no-cache --purge del .build-deps
    INFO[0030] | Created container 4d07a461385a (image sha256:55ae2)
    INFO[0184] Commit changes
    INFO[0187] | Result image is sha256:79f09                size=151.1 MB (+26.68 MB)
    INFO[0187] | Removing container 4d07a461385a
    INFO[0187] RUN mkdir -p /etc/ansible
    INFO[0188] | Created container 021968b10369 (image sha256:79f09)
    INFO[0188] Commit changes
    INFO[0190] | Result image is sha256:376dc                size=151.1 MB (+0 B)
    INFO[0190] | Removing container 021968b10369
    INFO[0191] COPY ui/resources/docker/ansible.cfg /etc/ansible/ansible.cfg
    INFO[0191] | Calculating tarsum for 1 files (5.437 kB total)
    INFO[0191] | Created container acf602cb1215 (image sha256:376dc)
    INFO[0191] | Uploading files to container acf602cb1215
    INFO[0191] Commit changes
    INFO[0193] | Result image is sha256:a3b7d                size=151.1 MB (+5.437 kB)
    INFO[0193] | Removing container acf602cb1215
    INFO[0193] COPY ui/resources/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
    INFO[0193] | Calculating tarsum for 1 files (5.844 kB total)
    INFO[0194] | Created container d2e1e94bba06 (image sha256:a3b7d)
    INFO[0194] | Uploading files to container d2e1e94bba06
    INFO[0194] Commit changes
    INFO[0196] | Result image is sha256:c0530                size=151.1 MB (+5.844 kB)
    INFO[0196] | Removing container d2e1e94bba06
    INFO[0196] RUN chmod +x /usr/local/bin/entrypoint.sh
    INFO[0197] | Created container 58814799d1c4 (image sha256:c0530)
    INFO[0197] Commit changes
    INFO[0199] | Result image is sha256:6fa79                size=151.1 MB (+0 B)
    INFO[0199] | Removing container 58814799d1c4
    INFO[0200] ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
    INFO[0200] Commit changes
    INFO[0200] | Created container dc4494fd062f (image sha256:6fa79)
    INFO[0202] | Result image is sha256:481e1                size=151.1 MB (+0 B)
    INFO[0202] | Removing container dc4494fd062f
    INFO[0202] COPY ui/resources/docker/torrent.sh /usr/local/bin/torrent.sh
    INFO[0202] | Calculating tarsum for 1 files (890 B total)
    INFO[0203] | Created container 9f15d6413cd2 (image sha256:481e1)
    INFO[0203] | Uploading files to container 9f15d6413cd2
    INFO[0203] Commit changes
    INFO[0205] | Result image is sha256:35f06                size=151.1 MB (+890 B)
    INFO[0205] | Removing container 9f15d6413cd2
    INFO[0205] COPY ui/resources/docker/ecs-install.2.5.1-local.installer-230.4.tgz /usr/local/src/ui.tgz
    INFO[0205] | Calculating tarsum for 1 files (3.958 MB total)
    INFO[0206] | Created container e6542b37ddc7 (image sha256:35f06)
    INFO[0206] | Uploading files to container e6542b37ddc7
    INFO[0206] Commit changes
    INFO[0208] | Result image is sha256:161f5                size=155.1 MB (+3.958 MB)
    INFO[0208] | Removing container e6542b37ddc7
    INFO[0208] ENV http_proxy=
    INFO[0208] ENV pip_proxy=
    INFO[0208] VOLUME [ "/opt", "/usr", "/var/log", "/root", "/etc" ]
    INFO[0208] LABEL VERSION=cache.local:5000/emccorp/ecs-install:2.5.1-local.installer-230.4
    INFO[0208] ENV VERSION=cache.local:5000/emccorp/ecs-install:2.5.1-local.installer-230.4
    INFO[0208] Commit changes
    INFO[0213] | Created container 7beb4650354e (image sha256:161f5)
    INFO[0216] | Result image is sha256:7bd3d                size=155.1 MB (+0 B)
    INFO[0216] | Removing container 7beb4650354e
    INFO[0217] TAG cache.local:5000/emccorp/ecs-install:2.5.1-local.installer-230.4
    INFO[0217] | Tag sha256:7bd3d -> cache.local:5000/emccorp/ecs-install:2.5.1-local.installer-230.4
    INFO[0217] Cleaning up
    INFO[0217] Successfully built sha256:7bd3d | final size 155.1 MB (+151.1 MB from the base image)
    > Tagging cache.local:5000/emccorp/ecs-install:2.5.1-local.installer-230.4 -> emccorp/ecs-install:latest

The new image is automatically tagged :latest in the local repository
and replaces any previous :latest images.

You'll then want to clean up the local Docker repository with this
command:

::

    [admin@installer-230 ECS-CommunityEdition]$ build_image --clean
    > Cleaning up...
    >      [build tmp containers]
    >      [ecs-install data containers]
    >      [exited containers]
    >      [dangling layers]

Making Quick Iterative Changes to an Existing ``ecs-install`` Image with ``update_image``
-----------------------------------------------------------------------------------------

Building an image can take a long time. If you have not made any changes
to files that are used in the ``docker build`` process, then you can
update an existing ``ecs-install`` data container with code changes
using the ``update_image`` macro:

::

    [admin@installer-230 ECS-CommunityEdition]$ update_image
    > Updating image: ecs-install
    > Build context is: local
    > Tunneling through proxy: cache.local:3128
    > Cleaning up...
    >      [build tmp containers]
    >      [ecs-install data containers]
    >      [exited containers]
    >      [dangling layers]
    > Collecting artifacts
    > UI is: ui/resources/docker/ecs-install.2.5.1-local.installer-230.5.tgz
    > Creating new data container
    > Image updated.

Quickly Testing Ansible Changes with ``testbook``
-------------------------------------------------

If you're working with Ansible within ECS Community Edition, you might
find yourself needing to test to see how your Ansible role is being
played from within the ``ecs-install`` image. You can do this by
modifying the files under the ``testing`` subdirectory of the Ansible
``roles`` directory: ``ui/ansible/roles/testing``

After making your changes, run ``update_image`` as discussed above, and
then run ``testbook`` to execute your role. The ``testbook`` command
will automatically initialize a new data container, configure access
with the install node, and test your role directives.
