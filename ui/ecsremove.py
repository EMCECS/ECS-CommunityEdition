#!/usr/bin/env python
# coding=utf-8
"""
basic text-based init
"""

import logging
import os
import subprocess
import shutil
import sys
import click
import tui
import yaml
from sarge import Capture, run, shell_format, capture_both, get_both

from tui.constants import *

# TAG: DevTest
# sys.dont_write_bytecode = True

"""
Globals
"""


"""
# Logging
"""


logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


"""
# Helpers
"""


def play(playbook, verbosity=0):

    if verbosity > 0:
        verb = "-{0}".format('v' * verbosity)
        cmd = shell_format('ansible-playbook {0} {1}.yml', verb, playbook)
    else:
        cmd = shell_format('ansible-playbook {0}.yml', playbook)

    if run(cmd, cwd=ansible_root).returncode > 0:
        click.echo('Operation failed.')
        return False
    else:
        return True


def purge_install_node():
    """
    Purges the install node cache
    """
    click.echo("Purging install node caches")
    sh = run('rm -rf {0}'.format(cache_root))
    sh = run('mkdir -p {0} {1}'.format(cache_root, ansible_facts))
    click.echo("OK")


def purge_data_nodes(conf):
    """
    Uninstalls ECS and purges the data node cache
    """
    playbook = 'clicmd_purge'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


"""
# Config
"""


class Conf(tui.Director):
    """
    Director subclass for
    """
    def __init__(self):
        tui.Director.__init__(self)


pass_conf = click.make_pass_decorator(Conf, ensure=True)


"""
# Commands
"""


@click.group(chain=True)
@click.option('-v', '--verbose', count=True, help="Use multiple times for more verbosity")
@pass_conf
def ecsremove(conf, verbose):
    """
    Command line interface to remove ECS bits
    """
    conf.config.verbosity = verbose


@ecsremove.command('purge-nodes', short_help='Uninstall ECS and purge artifacts from data nodes')
@pass_conf
def purge_nodes(conf):
    purge_data_nodes(conf)


@ecsremove.command('purge-installer', short_help='Purge caches from install node')
@pass_conf
def purge_installer(conf):
    purge_install_node()


@ecsremove.command('purge-all', short_help='Uninstall ECS and purge artifacts from all nodes')
@pass_conf
def purge_all(conf):
    purge_install_node()
    purge_data_nodes(conf)


if __name__ == '__main__':
    ecsremove()
