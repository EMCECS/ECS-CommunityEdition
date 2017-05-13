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
import sys
import click
import tui
import tui.tools
from tui.tools import o, die
import time
import simplejson
from sarge import Capture, run, shell_format, capture_both, get_both
from tui.defaults import *
from ecsclient.client import Client
from ecsclient.common.exceptions import ECSClientException

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
    api_verify_ssl = False

    def __init__(self):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        tui.Director.__init__(self)
        self.ecs = tui.ECSConf(self.deploy)
        self.api_root_user = self.ecs.get_root_user()
        self.api_root_pass = self.ecs.get_root_pass()
        # Default to the first data node listed
        self.api_endpoint = self.ecs.list_all_sp_nodes()[0]
        self.api_client = self._api_get_client()
        # self.expected_dt_total = self.ecs.get_expected_dts()
        self.expected_dt_total = 416

    def api_set_endpoint(self, api_endpoint):
        """
        Sets the API endpoint to use. default is random endpoint
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
        Returns an instance of ecsclient.client.Client
        """
        url = "{0}://{1}:{2}".format(API_PROTOCOL, self.api_endpoint, API_PORT)

        return Client('3',
                      username=self.api_root_user,
                      password=self.api_root_pass,
                      token_endpoint=url + '/login',
                      ecs_endpoint=url,
                      verify_ssl=self.api_verify_ssl,
                      request_timeout=self.api_timeout)

    def api_close(self):
        """
        Logs out and destroys the API instance
        """
        self.api_client.authentication.logout()
        del self.api_client

    def api_reset(self):
        """
        Resets the APIAdminClient instance
        """
        self.api_client = self._api_get_client()

    def diag_dt_get(self):
        """
        Returns the dt stats
        total_dt_num
        unknown_dt_num
        unready_dt_num
        """
        dt_diag_client = tui.ECSDiag(self.api_endpoint)
        return dt_diag_client.get_dt_status()

    def diag_dt_ready(self, footprint='small'):
        """
        Returns True of no dt unready and dt unknown, False otherwise
        """
        dt_data = self.diag_dt_get()
        if dt_data['unknown_dt_num'] > 0 \
                or dt_data['total_dt_num'] < self.ecs.get_dt_total(footprint) \
                or dt_data['unready_dt_num'] > 0:
            return False
        else:
            return True

    def diag_dt_status_text(self):
        """
        Get a status string
        :return: dt status string
        """
        try:
            dt_data = self.diag_dt_get()
            dt_string = "dt_total={} dt_unready={} dt_unknown={}".format(
                dt_data['total_dt_num'],
                dt_data['unready_dt_num'],
                dt_data['unknown_dt_num'])
        except KeyError:
            dt_string = "dt_query fail"

        return dt_string

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

    def api_task_get_status(self, task_id):
        pass

    def get_vdc_id_by_name(self, vdc_name):
        return self.api_client.vdc.get(name=vdc_name)['id']

    def get_vdc_secret(self, vdc_name):
        return self.api_client.vdc.get_local_secret_key()['key']

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


@ecsconfig.command('ping', short_help='Check ECS Management API Endpoint')
@click.option('-c', is_flag=True, help='Continuous ping')
@click.option('-w', default=10, help='(with -c) Seconds to wait between pings')
@click.option('-x', is_flag=True, help='Exit upon successful PONG')
@pass_conf
def ping(conf, c, w, x):
    """
    Ping ECS management API for connectivity
    :param conf: Click config object with helpers
    :param c: Click bool flag
    :param w: Click argument
    :param x: Click bool flag
    :return:
    """

    if c:
        msg = " (CTRL-C to break)"
    else:
        msg = ""
    o("Pinging endpoint {}...{}".format(conf.api_endpoint, msg))

    pinging = True
    while pinging is True:

        try:
            resp_dict = conf.api_client.user_info.whoami()
            if resp_dict is not None:
                if resp_dict['common_name'] is not None:
                    o('PONG: username={} {}'.format(resp_dict['common_name'], conf.diag_dt_status_text()))
                    if x:
                        sys.exit(0)
                else:
                    raise ECSClientException("Unexpected response from API")
        except requests.ConnectionError or httplib.HTTPException:
            o("FAIL: API service unavailable {}".format(conf.diag_dt_status_text()))
            try:
                del conf.api_client
                if not c:
                    sys.exit(1)
            except AssertionError:
                if not c:
                    sys.exit(1)
        except ECSClientException as e:
            if 'Connection refused' in e.message:
                o('FAIL: API service is not alive. This is likely temporary.')
            elif 'connection failed' in e.message:
                o('FAIL: API service is alive but ECS is not. This is likely temporary.')
            elif 'Invalid username or password' in e.message:
                o('FAIL: Invalid username or password. If ECS authsvc is bootstrapping, this is likely temporary.')
            elif 'Non-200' in e.message:
                o('FAIL: ECS API internal error. If ECS services are still bootstrapping, this is likely temporary.')
            else:
                o('FAIL: Unexpected response from API client: {0}'.format(e))
                if not c:
                    raise
        if not c:
            pinging = False
        if c:
            time.sleep(w)


@ecsconfig.command('licensing', short_help='Work with ECS Licenses')
@click.option('-l', is_flag=True, help='List current license installed in ECS')
@click.option('-a', is_flag=True, help='Install default ECS Community Edition license into ECS')
@click.option('-c', help='Install custom license into ECS from file at given path')
@pass_conf
def licensing(conf, l, a, c):

    def get_license():
        return conf.api_client.licensing.get_license()['license_text']

    def add_license(license_blob):
        # license_text is a global variable from defaults.py which
        # can be overridden.
        # o(license_blob)
        license_dict = {"license_text": license_blob.rstrip('\n')}
        return conf.api_client.licensing.add_license(license_dict)

    def add_default_license():
        return add_license(license_text)

    def add_custom_license(license_path):
        with open('{}'.format(license_path), 'r') as fp:
            license_blob = fp.read()
        return add_license(license_blob)

    # Select behavior
    if l:
        c = None
        a = False
        try:
            license_blob = get_license()
            o('Current license installed in ECS:')
            o(license_blob)
        except ECSClientException as e:
            die("Could not get license from ECS", e)

    if a:
        c = None
        try:
            license_blob = add_default_license()
            o('Added default license to ECS')
        except ECSClientException as e:
            die("Could not add default license", e)

    if c is not None:
        try:
            license_blob = add_custom_license(c)
            o('Added custom license to ECS')
        except IOError as e:
            die('Could not read custom license file {}:'.format(c), e)
        except ECSClientException as e:
            die("Could not add custom license", e)


@ecsconfig.command('trust', short_help='Work with ECS Certificates')
@click.option('-l', is_flag=True, help='List current cert installed in ECS')
@click.option('-x', is_flag=True, help='Generate and trust a new self-signed cert in ECS')
@click.option('-t', is_flag=True, help='Fetch and trust the current ECS cert')
@click.option('-c', help='Install custom x509 cert from file into ECS')
@click.option('-k', help='(with -c) Private key to use for custom cert')
@pass_conf
def trust(conf, l, x, t, c, k):

    def get_cert():
        return conf.api_client.certificate.get_certificate_chain()['chain']

    def install_cert(cert_chain=None, private_key=None, self_signed=False, ip_addresses=None):
        kwargs = {
            'cert_chain': cert_chain,
            'private_key': private_key,
            'selfsigned': self_signed,
            'ip_addresses': ip_addresses
        }
        return conf.api_client.certificate.set_certificate_chain(kwargs)['chain']

    def generate_self_signed_cert():
        return install_cert(self_signed=True, ip_addresses=conf.ecs.list_all_sp_nodes())

    def trust_cert(cert_chain):
        if cert_chain is not None:
            with open('{0}/ecscert.crt'.format(ssl_root), 'w') as fp:
                fp.write(str(cert_chain))
                stdout, stderr = get_both('update-ca-certificates')
            return stdout + stderr

    def install_custom_cert(cert_path, key_path):
        with open('{}'.format(cert_path), 'r') as fp:
            cert_blob = fp.read()

        with open('{}'.format(key_path), 'r') as fp:
            key_blob = fp.read()

        install_cert(cert_chain=cert_blob, private_key=key_blob)

    # Select behavior
    if l:
        try:
            o('Current ECS Certificate:')
            o(get_cert())
        except ECSClientException as e:
            die("Could not get certificate matter from ECS", e)

    if x:
        t = False
        c = None
        try:
            trust_cert(generate_self_signed_cert())
        except ECSClientException as e:
            die('Could not generate self-signed cert on ECS', e)

    if t:
        c = None
        o('Trusting current ECS certificate...')
        try:
            resp = trust_cert(get_cert())
            o(resp)
        except ECSClientException as e:
            die('Could get cert from ECS', e)
        except IOError as e:
            die('Could not add ECS cert to local store', e)

    if c is not None and k is not None:
        try:
            install_custom_cert(c, k)
        except (IOError, ECSClientException) as e:
            die("Could not install custom cert matter: {} {}:".format(c, k), e)


@ecsconfig.command('sp', short_help='Work with ECS Storage Pools')
@click.option('-l', is_flag=True, help='List known SP configs')
@click.option('-r', is_flag=True, help='Get current SP configs from ECS')
@click.option('-a', is_flag=True, help="Add all SPs to ECS")
@click.option('-n', default=None, help='Add the given SP to ECS')
@pass_conf
def sp(conf, l, r, a, n):
    def list_all():
        return conf.ecs.get_sp_names()

    def get_all():
        return conf.api_client.storage_pool.list()

    def sp_create(name, sp_ecs_options):
        """
        Create a storage pool
        :param name:
        :param sp_ecs_options: dict of kwargs
        :return: Storage Pool ID as URN
        """
        kwargs = {"name": name}
        kwargs.update(sp_ecs_options)
        #o('kwargs: {}'.format(kwargs))

        resp = conf.api_client.storage_pool.create(**kwargs)
        return resp['id']

    def sp_add_node(sp_id, node_ip):
        """
        Add given node to named storage pool
        :param sp_id: Storage Pool URN
        :param node_ip: IP address of node
        :return: Task object
        """

        node_dict = conf.ecs.get_node_options(node_ip)

        kwargs = {"name": node_ip,
                  "description": node_dict['description'],
                  "node_id": node_ip,
                  "storage_pool_id": sp_id}
        """
        def create(self, name, description, node_id, storage_pool_id):
        :param name: User provided name (not verified or unique)
        :param description: User provided description (not verified or unique)
        :param node_id: IP address for the commodity node
        :param storage_pool_id: Desired storage pool ID for creating data store
        :returns a task object
        """
        return conf.api_client.data_store.create(**kwargs)

    def add_one(name):
        o('Adding SP {}'.format(name))
        sp_id = sp_create(name, conf.ecs.sp_ecs_options(name))
        sp_tasks = []
        nodes = conf.ecs.get_sp_members(name)
        if nodes is not None:
            for node in nodes:
                o('Adding datastore node {} to {}'.format(node, name))
                conf.wait_for_dt_ready()
                # def api_sp_add_node(self, node_ip, sp_id, node_name=None, node_description=None):
                sp_tasks.append(sp_add_node(sp_id, node))
        return sp_tasks

    def add_all():
        storage_pools = conf.ecs.get_sp_names()
        if storage_pools is not None:
            sp_tasks = []
            for name in storage_pools:
                sp_tasks.extend(add_one(name))
            return sp_tasks
        return None

    if l:
        available_sp_configs = list_all()
        if available_sp_configs is not None:
            o("Available Storage Pool configurations:")
            for sp_name in available_sp_configs:
                o("\t{}".format(sp_name))
        else:
            o("No storage pool configurations are present.")

    if r:
        o('Storage Pools currently configured:')
        for sp_config in get_all():
            o("\t{}".format(sp_config['name']))

    if a:
        available_sp_configs = list_all()
        if available_sp_configs is not None:
            n = None
            conf.api_set_timeout(300)
            conf.api_close()
            conf.api_reset()
            tasks = add_all()
            #o(tasks)
            conf.api_set_timeout(API_TIMEOUT)
            conf.api_close()
            conf.api_reset()
        else:
            o('No storage pool configurations were provided in deploy.yml')

    if n is not None:
        conf.api_set_timeout(300)
        conf.api_close()
        conf.api_reset()
        tasks = add_one(n)
        #o(tasks)
        conf.api_set_timeout(API_TIMEOUT)
        conf.api_close()
        conf.api_reset()


@ecsconfig.command('vdc', short_help='Work with ECS Virtual Data Centers')
@click.option('-l', is_flag=True, help='List known VDC configs')
@click.option('-r', is_flag=True, help='Get current VDC configs from ECS')
@click.option('-a', is_flag=True, help="Add all VDCs to ECS")
@click.option('-n', default=None, help='Add the given VDC to ECS')
@pass_conf
def vdc(conf, l, r, a, n):
    """

    :param conf:
    :param l:
    :param r:
    :param a:
    :param n:
    :return:
    """
    def list_all():
        return conf.ecs.get_vdc_names()

    def get_all():
        return conf.api_client.vdc.list()

    def vdc_create(vdc_name):
        vdc_secret = conf.get_vdc_secret(vdc_name)
        if vdc_secret is None:
            raise AssertionError
            # vdc_secret = conf.ecs.gen_secret()

        endpoints = []
        for sp in conf.ecs.get_vdc_members(vdc_name):
            endpoints.extend(conf.ecs.get_sp_members(sp))
        endpoints = ','.join(endpoints)

        return conf.api_client.vdc.update('vdc',
                                          inter_vdc_endpoints=endpoints,
                                          secret_key=vdc_secret,
                                          new_name=vdc_name,
                                          management_endpoints=endpoints)

    def add_all():
        tasks = []

        for vdc_name in conf.ecs.get_vdc_names():
            o('\t{}'.format(vdc_name))
            conf.wait_for_dt_ready()
            tasks.append(vdc_create(vdc_name))
        return tasks

    def add_one(vdc_name):
        pass

    if l:
        available_vdc_configs = list_all()
        if available_vdc_configs is not None:
            o('Available VDC configurations:')
            for vdc_name in list_all():
                o('\t{}'.format(vdc_name))
        else:
            o('No VDC configurations are present in deploy.yml')

    if r:
        o('VDCs currently configured:')
        for vdc_name in get_all():
            o('\t{}'.format(vdc_name))

    if a:
        n = None
        available_vdc_configs = list_all()
        if available_vdc_configs is not None:
            o('Creating all VDCs...')
            # apparently doesn't return tasks
            tasks = add_all()
        else:
            o('No VDC configurations are present in deploy.yml')

    if n is not None:
        add_one(n)


@ecsconfig.command('rg', short_help='Work with ECS Replication Groups')
@click.option('-l', is_flag=True, help='List known RG configs')
@click.option('-r', is_flag=True, help='Get current RG configs from ECS')
@click.option('-a', is_flag=True, help="Add all RGs to ECS")
@click.option('-n', default=None, help='Add the given RG to ECS')
@pass_conf
def rg(conf, l, r, a, n):
    """

    :param conf:
    :param l:
    :param r:
    :param a:
    :param n:
    :return:
    """
    def list_all():
        return conf.ecs.get_rg_names()

    def get_all():
        return conf.api_client.replication_group.list()

    def add_rg(rg_name):
        o('Adding replication group {}'.format(rg_name))
        zone_mappings = []
        for vdc_name in conf.ecs.get_rg_members(rg_name):
            o('Generating zone mappings for {}/{}'.format(rg_name, vdc_name))
            vdc_id = conf.get_vdc_id_by_name(vdc_name)
            sp_records = conf.api_client.storage_pool.list(vdc_id=vdc_id)['varray']
            for sp_record in sp_records:
                o('\t{}'.format(sp_record['name']))
                zone_mappings.append((vdc_id, sp_record['id']))
        rg_options = conf.ecs.get_rg_options(rg_name)
        o('Applying mappings')
        resp = conf.api_client.replication_group.create(rg_name,
                                                        zone_mappings=zone_mappings,
                                                        description=rg_options['description'],
                                                        enable_rebalancing=rg_options['enable_rebalancing'],
                                                        allow_all_namespaces=rg_options['allow_all_namespaces'],
                                                        is_full_rep=rg_options['is_full_rep'])
        return resp

    def add_all():
        results = []
        for rg_name in conf.ecs.get_rg_names():
            results.append(add_rg(rg_name))
        return results

    if l:
        available_rg_configs = list_all()
        if available_rg_configs is not None:
            o('Available Replication Group Configurations:')
            for name in list_all():
                o('\t{}'.format(name))
        else:
            o('No replication group configurations in deploy.yml')

    if r:
        try:
            o('Replication Groups currently configured:')
            for name in get_all():
                o('\t{}'.format(name))
        except ECSClientException as e:
            die('')

    if a:
        n = None
        available_rg_configs = list_all()
        if available_rg_configs is not None:
            results = add_all()
            for result in results:
                o('Created replication group {}'.format(result['name']))
        else:
            o('No replication group configurations in deploy.yml')

    if n is not None:
        result = add_rg(n)
        o('Created replication group {}'.format(result['name']))


# @ecsconfig.command('namespace', short_help='Work with ECS Namespaces')
# @click.option('-l', is_flag=True, help='List known namespace configs')
# @click.option('-r', is_flag=True, help='Get current namespace configs from ECS')
# @click.option('-a', is_flag=True, help="Add all namespaces to ECS")
# @click.option('-n', default=None, help='Add the given namespace to ECS')
# @pass_conf
# def namespace(conf, l, r, a, n):
#     """
#     # BUG: Broken - doesn't build NS right
#     :param conf:
#     :param l:
#     :param r:
#     :param a:
#     :param n:
#     :return:
#     """
#     def list_all():
#         return conf.ecs.get_ns_names()
#
#     def get_all():
#         return conf.api_client.namespace.list()
#
#     def add_namespace(namespace_name):
#         o('Adding namespace {}'.format(namespace_name))
#         ns_dict = conf.ecs.get_ns_options(namespace_name)
#
#         kwargs = {"is_stale_allowed": ns_dict['is_stale_allowed'],
#                   "is_compliance_enabled": ns_dict['is_compliance_enabled'],
#                   "is_encryption_enabled": ns_dict['is_encryption_enabled'],
#                   "namespace_admins": ns_dict['namespace_admins'],
#                   "default_data_services_vpool": ns_dict['']}
#
#         return conf.api_client.namespace.create(namespace_name, **kwargs)
#
#     def add_all():
#         for namespace_name in list_all():
#             add_namespace(namespace_name)
#
#     if l:
#         available_rg_configs = list_all()
#         if available_rg_configs is not None:
#             o('Available Namespace configurations:')
#             for ns_name in list_all():
#                 o('\t{}'.format(ns_name))
#         else:
#             o('No namespace configurations in deploy.yml')
#     if r:
#         o('Namespaces currently configured:')
#         namespaces = get_all()
#         for ns_data in namespaces['namespace']:
#             o('\t{}'.format(ns_data['name']))
#     if a:
#         n = None
#         available_rg_configs = list_all()
#         if available_rg_configs is not None:
#             add_all()
#         else:
#             o('No namespace configurations in deploy.yml')
#     if n is not None:
#         add_namespace(n)


# @ecsconfig.command('object-user', short_help='Work with ECS Object Users')
# @click.option('-l', is_flag=True, help='List known object user configs')
# @click.option('-r', is_flag=True, help='Get all current object user configs from ECS')
# @click.option('-s', is_flag=True, help='Get current object user configs from ECS for given namespace')
# @click.option('-a', is_flag=True, help="Add all object user to ECS")
# @click.option('-n', default=None, help='Add the given object user to ECS')
# @pass_conf
# def object_user(conf, l, r, s, a, n):
#     def list_all():
#         pass
#
#     def get_all():
#         pass
#
#     def get_one():
#         pass
#
#     def add_all():
#         pass
#
#     def add_one(user_name):
#         pass
#
#     if l:
#         list_all()
#     if a:
#         n = None
#         add_all()
#     if n is not None:
#         add_one(n)
#
#
# @ecsconfig.command('management-user', short_help='Work with ECS Management Users')
# @click.option('-l', is_flag=True, help='List known management user configs')
# @click.option('-r', is_flag=True, help='Get all current management user configs from ECS')
# @click.option('-s', is_flag=True, help='Get current management user configs from ECS for given namespace')
# @click.option('-a', is_flag=True, help="Add all management user to ECS")
# @click.option('-n', default=None, help='Add the given management user to ECS')
# @pass_conf
# def management_user(conf, l, r, s, a, n):
#     def list_all():
#         pass
#
#     def get_all():
#         pass
#
#     def get_one():
#         pass
#
#     def add_all():
#         pass
#
#     def add_one(user_name):
#         pass
#
#     if l:
#         list_all()
#     if a:
#         n = None
#         add_all()
#     if n is not None:
#         add_one(n)
#
#
# @ecsconfig.command('bucket', short_help='Work with ECS Buckets')
# @click.option('-l', is_flag=True, help='List known bucket configs')
# @click.option('-r', is_flag=True, help='Get all current bucket configs from ECS')
# @click.option('-s', is_flag=True, help='Get current bucket configs from ECS for given namespace')
# @click.option('-a', is_flag=True, help="Add all buckets to ECS")
# @click.option('-n', default=None, help='Add the given bucket to ECS')
# @pass_conf
# def bucket(conf, l, r, s, a, n):
#     def list_all():
#         pass
#
#     def get_all():
#         pass
#
#     def get_one():
#         pass
#
#     def add_all():
#         pass
#
#     def add_one(bucket_name):
#         pass
#
#     if l:
#         list_all()
#     if a:
#         n = None
#         add_all()
#     if n is not None:
#         add_one(n)


if __name__ == '__main__':
    ecsconfig()
