# coding=utf-8
from setuptools import setup, find_packages

setup(
    name='ecsdeploy',
    version='2.11.0r',
    packages=find_packages(),
    scripts=['ui.py',
             'ecsdeploy.py',
             'ecsremove.py',
             'ecsconfig.py',
             'inventory.py'],
    include_package_data=True,
    package_data={'': ['*.yml']},
    author="Travis Wichert @EMC",
    author_email="padthaitofuhot@users.noreply.github.com",
    license="Proprietary, https://raw.githubusercontent.com/EMCECS/ECS-CommunityEdition/master/license.txt",
    url='https://github.com/EMCECS/ECS-CommunityEdition',
    install_requires=[
        'Click',
        'requests',
        'simplejson',
        'dotmap',
        'PyYAML',
        'Jinja2',
        'httplib2',
        'ipaddress',
        'futures',
        'urwid',
        'urwid-timed-progress',
        'pyopenssl',
        'sarge',
        'pykwalify',
        'python-ecsclient'
    ],
    entry_points='''
    [console_scripts]
    menu=ui:main
    ecsdeploy=ecsdeploy:ecsdeploy
    ecsremove=ecsremove:ecsremove
    ecsconfig=ecsconfig:ecsconfig
    inventory=inventory:inventory
    ''',
)
