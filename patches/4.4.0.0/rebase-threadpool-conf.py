#!/usr/bin/env python3
"""
Regenerate shared-threadpool-conf.xml for this release.

Starts from the base image's own copy of the file and applies only the
Community Edition thread pool adjustments, so beans introduced by the base
image are retained.

Usage:
    docker run --rm --entrypoint cat <reduced-image> \
        /opt/storageos/conf/shared-threadpool-conf.xml > base.xml
    ./rebase-threadpool-conf.py base.xml shared-threadpool-conf.xml
"""
import re
import sys

# Community Edition thread pool sizes, keyed by bean id. A pool's maximum must
# be at least its core size.
CE_OVERRIDES = {
    'unsealGeoHeartbeatThreadPoolConfig': {'maxPoolSize': '75'},
    'deleteJobThreadPoolConfig': {'corePoolSize': '250', 'maxPoolSize': '250'},
    'recoverReadDataThreadPoolConfig': {'maxPoolSize': '16'},
    'recoverWriteDataThreadPoolConfig': {'maxPoolSize': '16'},
}


def patch_bean(xml, bean_id, args):
    match = re.search(r'<bean id="%s".*?</bean>' % re.escape(bean_id), xml, re.S)
    if match is None:
        sys.exit("bean not found: %s" % bean_id)

    block = match.group(0)
    for name, value in args.items():
        pattern = r'(<constructor-arg name="%s" value=")[^"]*(")' % re.escape(name)
        if re.search(pattern, block) is None:
            sys.exit("bean %s has no constructor-arg %s" % (bean_id, name))
        block = re.sub(pattern, r'\g<1>%s\g<2>' % value, block)

    return xml[:match.start()] + block + xml[match.end():]


def check_pool_sizes(xml):
    """
    Return a list of beans whose maxPoolSize is below their corePoolSize.

    Such a pool cannot be constructed, so a service using it will not start.
    :param xml: contents of the thread pool configuration
    :return: list of (bean id, corePoolSize, maxPoolSize)
    """
    invalid = []
    for match in re.finditer(r'<bean id="([^"]+)"[^>]*>(.*?)</bean>', xml, re.S):
        bean_id, body = match.group(1), match.group(2)

        def value(name):
            found = re.search(r'name="%s" value="(-?\d+)"' % name, body)
            return int(found.group(1)) if found else None

        core, maximum = value('corePoolSize'), value('maxPoolSize')
        if core is not None and maximum is not None and maximum < core:
            invalid.append((bean_id, core, maximum))
    return invalid


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: %s <base.xml> <output.xml>" % sys.argv[0])

    src, dst = sys.argv[1], sys.argv[2]
    xml = open(src).read()

    bean_count = len(re.findall(r'<bean id="[^"]*ThreadPoolConfig"', xml))

    for bean_id, args in CE_OVERRIDES.items():
        xml = patch_bean(xml, bean_id, args)

    invalid = check_pool_sizes(xml)
    if invalid:
        for bean_id, core, maximum in invalid:
            print("%s: corePoolSize=%d exceeds maxPoolSize=%d" % (bean_id, core, maximum))
        sys.exit("refusing to write %s: add the beans above to CE_OVERRIDES" % dst)

    open(dst, 'w').write(xml)
    print("wrote %s (%d thread pool beans)" % (dst, bean_count))


if __name__ == '__main__':
    main()
