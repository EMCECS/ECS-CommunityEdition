#!/usr/bin/env python
# coding=utf-8

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import logging
import os
import subprocess
import sys
import pager
import textwrap
import click
import yaml
from sarge import run, shell_format

import tui
from tui.constants import *
from tui.tools import o

# TAG: DevTest
from pprint import pprint

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


"""
# Config
"""


class Conf(tui.Director):
    """
    Subclass Director for ecs-install cli tools
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
def ecsdeploy(conf, verbose):
    """
    Command line interface to Ecs-install installer
    """
    conf.config.verbosity = verbose


@ecsdeploy.command('load', short_help='Apply and validate deploy.yml')
@pass_conf
def load(conf):
    """
    Initializes or resets the installer idempotently.
    WARNING: Any previous deployment configuration will be replaced with
    the contents of deploy.yml.
    """
    try:
        init_paths = "mkdir -p {0} {1} {2} {3} {4} {5}".format(
            ssh_root, ssl_root, cache_root, log_root, ansible_conf, ansible_facts
        )
        sh = run(init_paths).returncode
        if sh > 0:
            raise IOError
    except IOError as e:
        click.echo(e)
        click.echo('Operation failed.')
        sys.exit(1)

    # Load up all the interesting stuff we know about.
    conf.load_config()
    conf.load_state()

    # Validate the deployment config file to before loading it
    try:
        conf.validate_deploy()
    except RuntimeError as e:
        click.echo(e.msg)
        click.echo('Operation failed.')
        sys.exit(1)

    # Catch all the noise here caused by deploy.yml weirdness because we can fix some
    # stuff later.
    try:
        conf.load_deploy()
    except IOError as e:
        logging.debug('IOError loading deploy.yml: {}'.format(e))
    except AttributeError as e:
        logging.debug('AttributeError loading deploy.yml: {}'.format(e))
    except AssertionError as e:
        logging.debug('AssertionError loading deploy.yml: {}'.format(e))

    try:
        if ('licensing' not in conf.state.toDict() or
                    conf.state.licensing.license_accepted is not True) and \
                ('licensing' not in conf.config.toDict() or
                         conf.config.licensing.license_accepted is not True) and \
                ('licensing' not in conf.deploy.toDict() or
                         conf.deploy.licensing.license_accepted is not True):

            try:
                # todo: Replace this with better wrapping
                # perhaps textwrap and pager modules.
                # beware the license has weird characters in it
                pager = subprocess.Popen(['less', '-~', '-M', '-I',
                                          conf.config.product.license_file],
                                         stdin=subprocess.PIPE, stdout=sys.stdout)
                pager.stdin.close()
                pager.wait()
                # with click.open_file(conf.config.product.license_file, 'r') as eula_file:
                #     eula_text = eula_file.read()

            except KeyboardInterrupt:
                pass

            promptstring = '> Do you accept the license? ["yes" or "no"]'
            result = click.prompt(promptstring)

            while result.lower() not in ('yes', 'no'):
                click.echo('You must type "yes" or "no" to continue.')
                result = click.prompt(promptstring)

            if result.lower() == 'no':
                click.echo('Understood. Exiting for now, but if you change your mind we will be here')
                click.echo('until you delete the files.')
                sys.exit(0)

            click.echo('Great, thanks for helping us keep the lawyers happy!')
            conf.state.licensing.license_accepted = True
            conf.save()

    except AttributeError as e:
        click.echo('Operation failed.')
        sys.exit(1)

    try:
        conf.load_deploy()
    except IOError as e:
        click.echo('Looks like you are starting a new deployment or else')
        click.echo('your {0} needs to be set up.'.format(conf.config.ui.host_deploy_file))
        click.echo('Please (re-)run setup or copy an existing deploy.yml to')
        click.echo('{0}.'.format(conf.config.ui.host_deploy_file))
        sys.exit(1)
    except AttributeError as e:
        click.echo('Operation failed.')
        sys.exit(1)

    all_vars = conf.config.toDict().copy()
    all_vars.update(conf.state.toDict())
    all_vars.update(conf.deploy.toDict())

    # pprint(all_vars)

    tui.JinjaCopy('{0}/caches.yml.j2'.format(ansible_setup_templates),
                  '{0}/caches.yml'.format(ansible_vars), all_vars)

    tui.JinjaCopy('{0}/autonames.yml.j2'.format(ansible_setup_templates),
                  '{0}/autonames.yml'.format(ansible_vars), all_vars)

    tui.JinjaCopy('{0}/all.j2'.format(ansible_setup_templates),
                  '{0}/all'.format(ansible_group_vars), all_vars)

    try:
        with open('{0}/all'.format(ansible_group_vars), 'a') as fp:
            fp.write('\n### Facts\n#\n')
            fp.write(yaml.dump(conf.deploy.facts.toDict(), default_flow_style=False))
    except IOError as e:
        click.echo(e)
        click.echo('Operation failed.')
        sys.exit(1)

    playbook = 'clicmd_access_host'
    if not play(playbook, 0):
        sys.exit(1)


@ecsdeploy.command('access', short_help='Configure ssh access to nodes')
@pass_conf
def access(conf):
    """
    Configure SSH access and setup ssh public key authentication
    on data nodes
    """
    playbook = 'clicmd_access'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


@ecsdeploy.command('cache', short_help='Build package cache')
@pass_conf
def cache(conf):
    """
    Build a deployment package cache for deploying from
    behind slow Internet links or into island environments.
    """

    # playbook = 'clicmd_access_host'
    # if not play(playbook, conf.config.verbosity):
    #     click.echo('Operation failed.')
    #     sys.exit(1)

    playbook = 'clicmd_cache'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


@ecsdeploy.command('check', short_help='Check data nodes to ensure they are in compliance')
@pass_conf
def check(conf):
    """
    Check data nodes to ensure they are in compliance before starting
    the deployment.
    """
    playbook = 'clicmd_preflight'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


@ecsdeploy.command('bootstrap', short_help='Install required packages on nodes')
@pass_conf
def bootstrap(conf):
    """
    Deploys ECS to all data nodes
    """

    playbook = 'clicmd_bootstrap'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)

@ecsdeploy.command('reboot', short_help='Reboot data nodes that need it')
@pass_conf
def reboot(conf):
    """
    Reboot data nodes that need rebooting, but not the install node.
    The install node must be manually rebooted if it is necessary.
    """
    playbook = 'clicmd_reboot'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)

@ecsdeploy.command('deploy', short_help='Deploy ECS to nodes')
@pass_conf
def deploy(conf):
    """
    Deploys ECS to all data nodes
    """

    playbook = 'clicmd_deploy'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)

@ecsdeploy.command('start', short_help='Start the ECS service')
@pass_conf
def start(conf):
    """
    Start the ECS service on all data nodes.
    """
    playbook = 'clicmd_start'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


@ecsdeploy.command('stop', short_help='Stop the ECS service')
@pass_conf
def stop(conf):
    """
    Stop the ECS service on all data nodes.
    """
    playbook = 'clicmd_stop'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


@ecsdeploy.command('disable-cache', short_help='Disable datanode package cache handling')
@pass_conf
def disable_cache(conf):
    """
    Disable datanode package cache handling.
    """
    playbook = 'clicmd_disable_cache'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


@ecsdeploy.command('enable-cache', short_help='Enable datanode package cache handling')
@pass_conf
def enable_cache(conf):
    """
    Enable datanode package cache handling.
    """
    playbook = 'clicmd_enable_cache'
    if not play(playbook, conf.config.verbosity):
        sys.exit(1)


@ecsdeploy.command('noop', short_help='noop')
@pass_conf
def enable_cache(conf):
    """
    Perform noop for some macros.
    """
    sys.exit(0)

if __name__ == '__main__':
    ecsdeploy()
