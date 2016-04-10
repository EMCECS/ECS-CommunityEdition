# coding=utf-8

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

"""
adsf
"""

import logging
import requests
import httplib
import os
import subprocess
import shutil
import sys
import click
import tui
import time
import yaml
import simplejson
from sarge import Capture, run, shell_format, capture_both, get_both
from ecsmgmt.ecs_admin_client import ECSAdminClient
from tui.defaults import *
from ecsmgmt.exception.ecsexception import ECSException

"""
# Logging
"""


logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


"""
# Helpers
"""


"""
# Config
"""


class Conf(tui.Director):
    """
    Subclass Director for ecs-install cli tools
    """
    api_root_user = None
    api_root_pass = None
    api_endpoint = None
    api_token = None
    api_client = None
    api_timeout = API_TIMEOUT
    api_retries = API_RETRIES

    def __init__(self):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        tui.Director.__init__(self)
        self.ecs = tui.ECSConf(self.deploy)
        self.api_root_user = self.ecs.get_root_user()
        self.api_root_pass = self.ecs.get_root_pass()
        self.api_endpoint = self.ecs.get_any_endpoint()
        self.api_client = self._api_get_client()

    def api_set_endpoint(self, api_endpoint):
        """
        Sets the API endpoint to use. Object default is random endpoint
        """
        self.api_endpoint = api_endpoint

    def api_set_timeout(self, timeout):
        """
        Sets the API timeout to <timeout> seconds
        :param timeout: <timeout> seconds
        """
        self.api_timeout = timeout

    def _api_get_client(self):
        """
        Returns an instance of ECSAdminClient
        """
        url = "{0}://{1}:{2}".format(API_PROTOCOL, self.api_endpoint, API_PORT)
        return ECSAdminClient(url, self.api_root_user, self.api_root_pass)

    def api_login(self):
        """
        Creates authentication session in ECSAdminClient object
        """
        self.api_token = self.api_client.login()

    def api_close(self):
        """
        Logs out and destroys the API instance
        """
        self.api_client.logout()
        del self.api_client

    def api_reset(self):
        """
        Resets the APIAdminClient instance
        """
        del self.api_client
        self.api_client = self._api_get_client()

    def diag_dt_unready_count(self):
        """
        Returns the count of dt_unready + dt_unknown
        """
        dt_diag = tui.ECSDiag(self.api_endpoint)
        dt_status = dt_diag.get_dt_status()
        return dt_status['unready_dt_num'] + dt_status['unknown_dt_num']

    def diag_dt_ready(self):
        """
        Returns True of no dt unready and dt unknown, False otherwise
        """
        if self.diag_dt_unready_count() > 0:
            return False
        else:
            return True

    def wait_for_dt_ready(self):
        """
        Loops until DT are ready or else timeout
        """
        tries = DIAGNOSTIC_RETRIES
        timeout = time.time() + DIAGNOSTIC_TIMEOUT
        while tries >= 0:
            while not time.time() < timeout:
                try:
                    assert self.diag_dt_ready() is True
                    return True
                except AssertionError:
                    time.sleep(1)
            tries -= 1
        return False

    def api_create_sp(self, sp_name, sp_ecs_options):
        # TODO: This is kinda hacky and gross
        create_kwargs = {"name": sp_name}
        create_kwargs.update(sp_ecs_options)
        resp_json = self.api_client.storage_pool().create_storage_pool(create_kwargs)

    def api_add_node_to_sp(self, sp_name, node):
        pass

    def api_create_vdc(self, vdc_name, vdc_members):
        pass


pass_conf = click.make_pass_decorator(Conf, ensure=True)


"""
# Commands
"""


@click.group(chain=True)
@click.option('-v', '--verbose', count=True, help="Use multiple times for more verbosity")
@pass_conf
def ecsconfig(conf, verbose):
    """
    Command line interface to configure ECS
    """
    conf.config.verbosity = verbose


# @ecsconfig.command('apply-config', short_help='Apply deploy.yml configuration to ECS')
# @pass_conf
# def apply_config(conf):
#     """
#     :param conf:
#     :type conf:
#     :return:
#     :rtype:
#     """



    # virtual_data_centers = conf.ecs.get_vdc_names()
    # if virtual_data_centers is not None:
    #     for vdc_name in virtual_data_centers:
    #         vdc_members = conf.ecs.get_vdc_members(vdc_name)
    #         conf.wait_for_dt_ready()
    #         conf.api_create_vdc(vdc_name, vdc_members)

    # replication_groups = conf.ecs.rg_names()
    # if replication_groups is not None:
    #     for rg_name in replication_groups:
    #         rg_members = conf.ecs.rg_members(rg_name)
    #         conf.wait_for_dt_ready()
    #         conf.api_create_rg(rg_name, rg_members)



@ecsconfig.command('add-sp', short_help='Add Storage Pools to ECS')
@click.option('-a', is_flag=True, default=False, help="Add all storage pools")
@click.option('-l', is_flag=True, default=True, help='List known storage pool configs')
@click.option('-n', default=None, help='The name of a storage pool to add')
@pass_conf
def add_sp(conf, a, l, n):

    if a:
        l = False
        n = None
        conf.api_login()
        storage_pools = conf.ecs.get_sp_names()
        if storage_pools is not None:
            for sp_name in storage_pools:

                conf.api_create_sp(sp_name, conf.ecs.sp_ecs_options(sp_name))

                data_stores = conf.ecs.get_sp_members(sp_name)
                if data_stores is not None:
                    for data_store in data_stores:
                        conf.wait_for_dt_ready()

                        conf.api_add_node_to_sp(sp_name, data_store)

    elif n is not None:
        a = False
        l = False
        sp_name = n
        conf.api_login()
        conf.api_create_sp(sp_name, conf.ecs.sp_ecs_options(sp_name))

        data_stores = conf.ecs.get_sp_members(sp_name)
        if data_stores is not None:
            for data_store in data_stores:
                conf.wait_for_dt_ready()

                conf.api_add_node_to_sp(sp_name, data_store)
    else:
        click.echo("Available Storage Pool configurations: ")
        for sp in conf.ecs.get_sp_names():
            click.echo("    {}".format(sp))
        sys.exit(0)



@ecsconfig.command('add-license', short_help='Add license to ECS')
@pass_conf
def add_license(conf):
    """
    Adds a license to a running ECS instance
    """
    # Add license
    click.echo('Updating ECS license...')
    license_dict = {"license_text": license_text}
    conf.api_login()
    try:
        if conf.api_client.license().add_license(license_dict):
            click.echo('OK')
    except ECSException or httplib.HTTPException:
        click.echo('Exception caught in ECS API.')


@ecsconfig.command('ping', short_help='Perform API endpoint check on ECS')
@click.option('--wait', is_flag=True, default=False)
@pass_conf
def ping(conf, wait):
    """
    :param conf:
    :type conf:
    :return:
    :rtype:
    """
    click.echo("Pinging random endpoint {}...".format(conf.api_endpoint))
    # click.echo("This can take a while during storage provisioning.")
    try:
        conf.api_login()
    except requests.ConnectionError or httplib.HTTPException:
        click.echo("FAIL: API service unavailable dt_unready={0}".format(conf.diag_dt_unready_count()))
        try:
            del conf.api_client
            sys.exit(1)
        except AssertionError:
            sys.exit(1)
    except ECSException as e:
        click.echo('Caught an unexpected exception in ECS API: {0}'.format(e))
        raise

    if conf.api_token is not None:
        click.echo('PONG: dt_unready={0} token={1}'.format(conf.diag_dt_unready_count(), conf.api_token))
        sys.exit(0)
    else:
        click.echo('API could not be reached. Check exception.')
        sys.exit(1)


@ecsconfig.command('trust-ecs', short_help='Fetch and trust the current ECS cert')
@pass_conf
def trust_ecs(conf):
    """
    :param conf:
    :type conf:
    :return:
    :rtype:
    """
    click.echo('Fetching ECS Certificate...')
    conf.api_login()
    cert_material = conf.api_client.certificate().getCertificateChain()['chain']

    # click.echo(cert_material)
    if cert_material is not None:

        try:
            with open('{0}/ecscert.crt'.format(ssl_root), 'w') as fp:
                fp.write(str(cert_material))
        except IOError as e:
            click.echo(e)
            click.echo('Operation failed.')
            conf.api_close()
            sys.exit(1)

        result = get_both('update-ca-certificates')

        click.echo("ECS certificate is now trusted.")
    else:
        click.echo('Could not get certificate from ECS. Try again later.')

if __name__ == '__main__':
    ecsconfig()
