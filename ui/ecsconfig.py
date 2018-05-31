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
This script configures various ECS structures according to the
deployment map in deploy.yml.
"""

import logging
import requests
import httplib
import os
import sys
import click
import tui
import tui.tools
from tui.tools import o, die, logobj
import time
import simplejson
from sarge import Capture, run, shell_format, capture_both, get_both
from tui.constants import *
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

DEBUG = True


def debug(msg):
    if DEBUG:
        o(msg)


"""
# Config
"""


class Conf(tui.Director):
    """
    Subclass Director for ecs-install cli tools
    """
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
        self.api_set_endpoint(self.ecs.get_vdc_endpoint(self.ecs.get_vdc_primary()))
        self.api_client = self._api_get_client()
        # self.expected_dt_total = self.ecs.get_expected_dts()
        self.expected_dt_total = 416

    def api_set_endpoint(self, api_endpoint):
        """
        Sets the API endpoint to use. default is random endpoint
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        logobj(api_endpoint)
        self.api_endpoint = api_endpoint

    def api_set_timeout(self, timeout):
        """
        Sets the API timeout to <timeout> seconds
        :param timeout: <timeout> seconds
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        logobj(timeout)
        self.api_timeout = timeout

    def _api_get_client(self):
        """
        Returns an instance of ecsclient.client.Client
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        url = "{0}://{1}:{2}".format(API_PROTOCOL, self.api_endpoint, API_PORT)
        logobj(url)
        return Client('3',
                      username=self.ecs.get_root_user(),
                      password=self.ecs.get_root_pass(),
                      token_endpoint=url + '/login',
                      ecs_endpoint=url,
                      verify_ssl=self.api_verify_ssl,
                      request_timeout=self.api_timeout)

    def api_reset(self):
        """
        Resets the APIAdminClient instance
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        try:
            self.api_client.authentication.logout()
        except Exception:
            pass

        try:
            del self.api_client
        except Exception:
            pass

        self.api_client = self._api_get_client()

    def diag_dt_get(self):
        """
        Returns the dt stats
        total_dt_num
        unknown_dt_num
        unready_dt_num
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        dt_diag_client = tui.ECSDiag(self.api_endpoint)
        return dt_diag_client.get_dt_status()

    def diag_dt_ready(self, footprint='small'):
        """
        Returns True of no dt unready and dt unknown, False otherwise
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        dt_data = self.diag_dt_get()
        if dt_data['unknown_dt_num'] > 0 \
                or dt_data['total_dt_num'] < self.ecs.get_dt_total(footprint) \
                or dt_data['unready_dt_num'] > 0:
            return False
        else:
            return True

    def diag_dt_status(self, dt_data=None):
        """
        Get a status string
        :return: dt status string
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        dt_string = None
        diag_success = False

        if dt_data is None:
            try:
                dt_data = self.diag_dt_get()
            except Exception as e:
                dt_string = "dt_query fail: {}".format(e)
                diag_success = False

        if dt_string is None:
            try:
                dt_string = "diag_endpoint={} dt_total={} dt_unready={} dt_unknown={}".format(
                    dt_data['endpoint'],
                    dt_data['total_dt_num'],
                    dt_data['unready_dt_num'],
                    dt_data['unknown_dt_num'])
                diag_success = True
            except Exception as e:
                dt_string = "dt_query fail: {}".format(e)
                diag_success = False

        return {'status': diag_success,
                'text': dt_string}

    def wait_for_dt_ready(self):
        """
        Loops until DT are ready or else timeout
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
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
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        pass

    def get_vdc_id_by_name(self, vdc_name):
        """
        Get the VDC ID of the VDC named vdc_name
        :param vdc_name: name of the deploy.yml VDC
        :return: VDC ID
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        return self.api_client.vdc.get(name=vdc_name)['id']

    def get_vdc_secret_by_name(self, vdc_name):
        """
        Get the VDC Secret Key of the VDC named vdc_name from the top node in that VDC
        :param vdc_name: name of the deploy.yml VDC
        :return: VDC Secret Key
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.api_set_endpoint(self.ecs.get_vdc_endpoint(vdc_name))
        self.api_reset()
        return self.api_client.vdc.get_local_secret_key()['key']

    def get_rg_id_by_name(self, rg_name):
        """
        Get the RG ID of the RG named rg_name
        :param rg_name: name of the deploy.yml RG
        :return: RG ID
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        rg_id_list = [x['id'] for x in self.api_client.replication_group.list()['data_service_vpool'] if x['name'] == rg_name]
        if len(rg_id_list) > 0:
            return rg_id_list[0]
        else:
            return False


pass_conf = click.make_pass_decorator(Conf, ensure=True)


"""
# Commands
"""


@click.group(chain=True)
@click.option('-v', '--verbose', count=True, help="Use multiple times for more verbosity")
@pass_conf
def ecsconfig(conf, verbose):
    """
    Command line interface to configure ECS from declarations in deploy.yml
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


@ecsconfig.command('ping', short_help='Check ECS Management API Endpoint(s)')
@click.option('-c', is_flag=True, help='Continuous ping')
@click.option('-w', default=10, help='(with -c) Seconds to wait between pings')
@click.option('-x', is_flag=True, help='Exit upon successful PONG')
@pass_conf
def ping(conf, c, w, x):
    """
    Check ECS Management API Endpoint(s)
    """
    """
    Ping ECS management API for connectivity
    :param conf: Click object containing the configuration
    :param c: continuous ping
    :param w: (with -c) seconds to wait between pings
    :param x: exit upon successful PONG
    :return: retval
    """

    def do_ping():
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
                        dt_status = conf.diag_dt_status()
                        if x:
                            if dt_status['status'] is True:
                                pinging = False
                                o('PONG: api_endpoint={} username={} {}'.format(conf.api_endpoint,
                                                                                resp_dict['common_name'],
                                                                                dt_status['text']))
                            else:
                                pinging = True
                                o('WAIT: api_endpoint={} username={} {}'.format(conf.api_endpoint,
                                                                                resp_dict['common_name'],
                                                                                dt_status['text']))
                    else:
                        raise ECSClientException("Unexpected response from API")
            except requests.ConnectionError or httplib.HTTPException:
                dt_status = conf.diag_dt_status()
                o("FAIL: API service unavailable {}".format(dt_status['text']))
                try:
                    del conf.api_client
                    if not c:
                        sys.exit(1)
                except AssertionError:
                    if not c:
                        sys.exit(1)
            except ECSClientException as e:
                if 'Connection refused' in e.message:
                    o('WAIT: API service is not alive. This is likely temporary.')
                elif 'connection failed' in e.message:
                    o('WAIT: API service is alive but ECS is not. This is likely temporary.')
                elif 'Invalid username or password' in e.message:
                    o('WAIT: Invalid username or password. If ECS authsvc is bootstrapping, this is likely temporary.')
                elif 'Non-200' in e.message:
                    o('WAIT: ECS API internal error. If ECS services are still bootstrapping, this is likely temporary.')
                elif 'Read timed out' in e.message:
                    o('WAIT: ECS API timed out.  If ECS services are still bootstrapping, this is likely temporary.')
                else:
                    o('FAIL: Unexpected response from API client: {0}'.format(e))
                    if not c:
                        raise
            if not c:
                pinging = False
            if c and pinging is True:
                time.sleep(w)

    vdc_list = conf.ecs.get_vdc_names()

    if vdc_list is not None:
        # o('vdc_list={}'.format(vdc_list))
        if len(vdc_list) > 1:
            o('Pinging endpoints for {} VDCs:'.format(len(vdc_list)))
            for vdc in vdc_list:
                o('\t{}: {}'.format(vdc, conf.ecs.get_vdc_endpoint(vdc)))
            endpoint_list = [conf.ecs.get_vdc_endpoint(vdc) for vdc in vdc_list]
            logobj(endpoint_list)
        else:
            endpoint_list = [conf.ecs.get_vdc_endpoint(conf.ecs.get_vdc_primary())]
            logobj(endpoint_list)

        for endpoint in endpoint_list:
            conf.api_set_endpoint(endpoint)
            conf.api_reset()
            do_ping()

    else:
        do_ping()

@ecsconfig.command('licensing', short_help='Work with ECS Licenses')
@click.option('-l', is_flag=True, help='List current license installed in ECS')
@click.option('-a', is_flag=True, help='Install default ECS Community Edition license into ECS')
@click.option('-c', help='Install custom license into ECS from file at given path')
@pass_conf
def licensing(conf, l, a, c):
    """
    Work with ECS Licensing
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param a: add all known configurations of this abstraction
    :param c: add a single custom configuration of this abstraction
    :return: retval
    """
    def get_license():
        return conf.api_client.licensing.get_license()['license_text']

    def add_license(license_blob):
        # license_text is a global variable from constants.py which
        # can be overridden.
        # o(license_blob)
        #license_dict = {"license_text": license_blob.rstrip('\n')}
        # License has to be uploaded to every VDC's top endpoint
        result_list = []
        for vdc in conf.ecs.get_vdc_names():
            o('Adding licensing to VDC: {}'.format(vdc))
            conf.api_endpoint = conf.ecs.get_vdc_endpoint(vdc)
            conf.api_reset()
            result_list.extend(conf.api_client.licensing.add_license(license_blob))
            o('\tOK')
        return result_list

    def add_default_license():
        o('Using default license')
        return add_license(license_text)

    def add_custom_license(license_path):
        o('Using custom license from {}'.format(license_path))
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
        o('Installing licensing in ECS VDC(s)')
        c = None
        try:
            license_blob = add_default_license()
            o('Added default license to ECS')
        except ECSClientException as e:
            die("Could not add default license", e)

    if c is not None:
        o('Installing licensing in ECS VDC(s)')
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
    """
    Work with ECS Certificates
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list current cert installed in ECS
    :param x: generate and trust a new self-signed cert in ECS
    :param t: Fetch and trust the current ECS cert
    :param c: Install custom x509 cert from file into ECS
    :param k: (with -c) Private key to use for custom cert
    :return: retval
    """
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
    """
    Work with ECS Storage Pools
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param r: list instances of this abstraction configured on ECS
    :param a: add all known configurations of this abstraction
    :param n: add a single known configuration of this abstraction
    :return: retval
    """
    def list_all():
        return conf.ecs.get_sp_names()

    def get_all():
        return conf.api_client.storage_pool.list()

    def sp_create(name, sp_ecs_options):
        """
        Create a storage pool
        :param name: name of storage pool
        :param sp_ecs_options: dict of kwargs
        :return: Storage Pool ID as URN
        """
        kwargs = {"name": name}
        kwargs.update(sp_ecs_options)
        resp = conf.api_client.storage_pool.create(**kwargs)
        return resp['id']

    def sp_add_node(sp_id, node_ip):
        """
        Add given node to named storage pool
        :param sp_id: Storage Pool URN
        :param node_ip: IP address of node
        :return: retval
        """

        node_dict = conf.ecs.get_node_options(node_ip)

        # Obtain the nodeId from the node IP address
        # In ECS < 3.1, nodeId is the IP address
        # In ECS >= 3.1, nodeId is an autogenerated UUID
        nodes = conf.api_client.node.list()
        node_info = list(filter(lambda x: x['ip'] == node_ip, nodes['node']))

        kwargs = {"name": node_ip,
                  "description": node_dict['description'],
                  "node_id": node_info[0]['nodeid'],
                  "storage_pool_id": sp_id}
        """
        def create(self, name, description, node_id, storage_pool_id):
        :param name: User provided name (not verified or unique)
        :param description: User provided description (not verified or unique)
        :param node_id: ID of the commodity node
        :param storage_pool_id: Desired storage pool ID for creating data store
        :returns a task object
        """
        return conf.api_client.data_store.create(**kwargs)

    def add_one(name):
        vdc_name = conf.ecs.get_sp_vdc(name)
        o('Creating Storage Pool: {}/{}'.format(vdc_name, name))

        # Set the correct endpoint for this VDC/SP combo
        conf.api_set_endpoint(conf.ecs.get_vdc_endpoint(vdc_name))
        conf.api_reset()
        conf.wait_for_dt_ready()

        sp_id = sp_create(name, conf.ecs.sp_ecs_options(name))
        sp_tasks = []
        o('\tOK')

        nodes = conf.ecs.get_sp_members(name)

        if nodes is not None:
            o('Adding Data Stores to Storage Pool:')
            for node in nodes:
                o('\t{}/{}/{}'.format(vdc_name, name, node))
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
                o("\t{}: '{}'".format(conf.ecs.get_sp_vdc(sp_name), sp_name))
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
            conf.api_reset()
            tasks = add_all()
            #o(tasks)
            conf.api_set_timeout(API_TIMEOUT)
            conf.api_reset()
        else:
            o('No storage pool configurations were provided in deploy.yml')

    if n is not None:
        conf.api_set_timeout(300)
        conf.api_reset()
        tasks = add_one(n)
        #o(tasks)
        conf.api_set_timeout(API_TIMEOUT)
        conf.api_reset()


# @ecsconfig.command('ds', short_help='Work with ECS Data Stores')
# @click.option('-l', is_flag=True, help='List known DS configs')
# @click.option('-r', is_flag=True, help='Get current DS configs from ECS')
# @click.option('-a', is_flag=True, help="Add all DSs to ECS")
# @click.option('-n', default=None, help='Add the given DS to ECS')
# @pass_conf
# def ds(conf, l, r, a, n):
#     """
#     Work with a collection of ECS abstractions
#     :param conf: Click object containing the configuration
#     :param l: list known configurations of this abstraction
#     :param r: list instances of this abstraction configured on ECS
#     :param a: add all known configurations of this abstraction
#     :param n: add a single known configuration of this abstraction
#     :return: retval
#     """
#     def list_all():
#         return conf.ecs.get_sp_names()
#
#     def get_all():
#         return conf.api_client.storage_pool.list()
#
#     def sp_create(name, sp_ecs_options):
#         """
#         Create a storage pool
#         :param name:
#         :param sp_ecs_options: dict of kwargs
#         :return: Storage Pool ID as URN
#         """
#         kwargs = {"name": name}
#         kwargs.update(sp_ecs_options)
#         #o('kwargs: {}'.format(kwargs))
#
#         resp = conf.api_client.storage_pool.create(**kwargs)
#         return resp['id']
#
#     def sp_add_node(sp_id, node_ip):
#         """
#         Add given node to named storage pool
#         :param sp_id: Storage Pool URN
#         :param node_ip: IP address of node
#         :return: retval
#         """
#
#         node_dict = conf.ecs.get_node_options(node_ip)
#
#         kwargs = {"name": node_ip,
#                   "description": node_dict['description'],
#                   "node_id": node_ip,
#                   "storage_pool_id": sp_id}
#         """
#         def create(self, name, description, node_id, storage_pool_id):
#         :param name: User provided name (not verified or unique)
#         :param description: User provided description (not verified or unique)
#         :param node_id: IP address for the commodity node
#         :param storage_pool_id: Desired storage pool ID for creating data store
#         :returns a task object
#         """
#         return conf.api_client.data_store.create(**kwargs)
#
#     def add_one(name):
#         o('Adding SP {}'.format(name))
#         sp_id = sp_create(name, conf.ecs.sp_ecs_options(name))
#         sp_tasks = []
#         nodes = conf.ecs.get_sp_members(name)
#         if nodes is not None:
#             for node in nodes:
#                 o('Adding datastore node {} to {}'.format(node, name))
#                 conf.wait_for_dt_ready()
#                 # def api_sp_add_node(self, node_ip, sp_id, node_name=None, node_description=None):
#                 sp_tasks.append(sp_add_node(sp_id, node))
#         return sp_tasks
#
#     def add_all():
#         storage_pools = conf.ecs.get_sp_names()
#         if storage_pools is not None:
#             sp_tasks = []
#             for name in storage_pools:
#                 sp_tasks.extend(add_one(name))
#             return sp_tasks
#         return None
#
#     if l:
#         available_sp_configs = list_all()
#         if available_sp_configs is not None:
#             o("Available Storage Pool configurations:")
#             for sp_name in available_sp_configs:
#                 o("\t{}".format(sp_name))
#         else:
#             o("No storage pool configurations are present.")
#
#     if r:
#         o('Storage Pools currently configured:')
#         for sp_config in get_all():
#             o("\t{}".format(sp_config['name']))
#
#     if a:
#         available_sp_configs = list_all()
#         if available_sp_configs is not None:
#             n = None
#             conf.api_set_timeout(300)
#             conf.api_reset()
#             tasks = add_all()
#             #o(tasks)
#             conf.api_set_timeout(API_TIMEOUT)
#             conf.api_reset()
#         else:
#             o('No storage pool configurations were provided in deploy.yml')
#
#     if n is not None:
#         conf.api_set_timeout(300)
#         conf.api_reset()
#         tasks = add_one(n)
#         #o(tasks)
#         conf.api_set_timeout(API_TIMEOUT)
#         conf.api_reset()
#

@ecsconfig.command('vdc', short_help='Work with ECS Virtual Data Centers')
@click.option('-l', is_flag=True, help='List known VDC configs')
@click.option('-r', is_flag=True, help='Get current VDC configs from ECS')
@click.option('-a', is_flag=True, help="Add all VDCs to ECS")
@click.option('-n', default=None, help='Add the given VDC to ECS')
@click.option('-p', is_flag=True, help="Ping Remote VDCs for active status")
@pass_conf
def vdc(conf, l, r, a, n, p):
    """
    Work with ECS Virtual Data Centers
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param r: list instances of this abstraction configured on ECS
    :param a: add all known configurations of this abstraction
    :param n: add a single known configuration of this abstraction
    :param p: Ping Remote VDCs for active status
    :return: retval
    """
    def list_all():
        return conf.ecs.get_vdc_names()

    def get_all():
        return conf.api_client.vdc.list()

    def vdc_create(vdc_name):
        vdc_secret = conf.get_vdc_secret_by_name(vdc_name)
        if vdc_secret is None:
            raise AssertionError
            # vdc_secret = conf.ecs.gen_secret()

        endpoints_list = []
        for sp in conf.ecs.get_vdc_members(vdc_name):
            endpoints_list.extend(conf.ecs.get_sp_members(sp))
        endpoints = ','.join(endpoints_list)

        # Always create VDCs from the top (first listed) VDC using the secret keys acquired
        # from remote VDCs.  This allows VDCs to be coordinated from one endpoint for other
        # constructs, such as geo replication.
        # Always use get_vdc_primary() to find the top VDC
        conf.api_set_endpoint(conf.ecs.get_vdc_endpoint(conf.ecs.get_vdc_primary()))
        conf.api_reset()

        return conf.api_client.vdc.update('vdc',
                                          inter_vdc_endpoints=endpoints,
                                          inter_vdc_cmd_endpoints=endpoints,
                                          secret_key=vdc_secret,
                                          new_name=vdc_name,
                                          management_endpoints=endpoints)

    def add_one(vdc_name):
        conf.wait_for_dt_ready()
        o('\t{}'.format(vdc_name))
        return vdc_create(vdc_name)

    def add_all():
        tasks = []

        for vdc_name in conf.ecs.get_vdc_names():
            tasks.append(add_one(vdc_name))
        return tasks

    def get_status(vdc_name):
        try:
            vdc_id = conf.get_vdc_id_by_name(vdc_name)
            vdc_dict = conf.api_client.vdc.get(vdc_id)

            # First see if the remote VDC storage pools are visible from this endpoint
            try:
                storage_pool_visibility_probe = conf.api_client.storage_pool.list(vdc_id=vdc_id)
            except Exception:
                return False

            # Second see if any VDC statuses are problematic
            if vdc_dict['permanentlyFailed'] is True:
                return False
            elif vdc_dict['inactive'] is True:
                return False
            else:
                return True

        except Exception:
            return False

    def ping_vdcs(vdc_list):
        status = True
        for vdc_name in vdc_list:
            o('Checking {}: '.format(vdc_name), nl=False)
            if get_status(vdc_name) is False:
                o('\tWAIT: VDC still onlining...')
                status = False
            else:
                o('\tOK: VDC online')
        return status

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

    if p:
        o('Waiting for all VDCs to online and become active...')
        while not ping_vdcs(list_all()):
            o('Retrying...')
            time.sleep(10)

    if a:
        n = None
        available_vdc_configs = list_all()
        if available_vdc_configs is not None:
            o('Creating all VDCs...')
            # apparently doesn't return tasks
            tasks = add_all()
            o('Created all VDCs')
        else:
            o('No VDC configurations are present in deploy.yml')

    if n is not None:
        o('Creating VDC...')
        add_one(n)
        o('Created VDC')


@ecsconfig.command('rg', short_help='Work with ECS Replication Groups')
@click.option('-l', is_flag=True, help='List known RG configs')
@click.option('-r', is_flag=True, help='Get current RG configs from ECS')
@click.option('-a', is_flag=True, help="Add all RGs to ECS")
@click.option('-n', default=None, help='Add the given RG to ECS')
@pass_conf
def rg(conf, l, r, a, n):
    """
    Work with ECS Replication Groups
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param r: list instances of this abstraction configured on ECS
    :param a: add all known configurations of this abstraction
    :param n: add a single known configuration of this abstraction
    :return: retval
    """
    def list_all():
        return conf.ecs.get_rg_names()

    def get_all():
        return conf.api_client.replication_group.list()['data_service_vpool']

    def add_rg(rg_name):
        o('Creating replication group {}'.format(rg_name))
        zone_mappings = []
        for vdc_name in conf.ecs.get_rg_members(rg_name):
            o('\tGenerating zone mappings for {}/{}'.format(rg_name, vdc_name))
            vdc_id = conf.get_vdc_id_by_name(vdc_name)
            sp_records = conf.api_client.storage_pool.list(vdc_id=vdc_id)['varray']
            for sp_record in sp_records:
                o('\t{}'.format(sp_record['name']))
                zone_mappings.append((vdc_id, sp_record['id']))
        rg_options = conf.ecs.get_rg_options(rg_name)
        o('\tApplying mappings')
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
            o('\tOK')
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
            for rg_dict in get_all():
                o('\t{}'.format(rg_dict['name']))
        except ECSClientException as e:
            die('')

    if a:
        n = None
        available_rg_configs = list_all()
        if available_rg_configs is not None:
            results = add_all()
            o('Created all Replication Groups')
        else:
            o('No replication group configurations in deploy.yml')

    if n is not None:
        result = add_rg(n)
        o('Created replication group {}'.format(result['name']))


@ecsconfig.command('namespace', short_help='Work with ECS Namespaces')
@click.option('-l', is_flag=True, help='List known namespace configs')
@click.option('-r', is_flag=True, help='Get current namespace configs from ECS')
@click.option('-a', is_flag=True, help="Add all namespaces to ECS")
@click.option('-n', default=None, help='Add the given namespace to ECS')
@pass_conf
def namespace(conf, l, r, a, n):
    """
    Work with ECS Namespaces
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param r: list instances of this abstraction configured on ECS
    :param a: add all known configurations of this abstraction
    :param n: add a single known configuration of this abstraction
    :return: retval
    """
    def list_all():
        return conf.ecs.get_ns_names()

    def get_all():
        return conf.api_client.namespace.list()

    def namespace_exists(name):
        if name in list_all():
            return True
        return False

    def add_namespace(namespace_name):
        ns_dict = conf.ecs.get_ns_dict(namespace_name)
        default_data_services_vpool = [
            x['id']
            for x
            in conf.api_client.replication_group.list()['data_service_vpool']
            if x['name'] == ns_dict['replication_group']
        ][0]
        kwargs = {"is_stale_allowed": ns_dict['is_stale_allowed'],
                  "is_compliance_enabled": ns_dict['is_compliance_enabled'],
                  "is_encryption_enabled": ns_dict['is_encryption_enabled'],
                  "namespace_admins": ns_dict['administrators'],
                  "default_data_services_vpool": default_data_services_vpool}
        return conf.api_client.namespace.create(namespace_name, **kwargs)

    def add_all():
        o('Creating all Namespaces')
        for namespace_name in list_all():
            o('Adding namespace {}'.format(namespace_name))
            add_namespace(namespace_name)
            o('\tOK')

    if l:
        available_ns_configs = list_all()
        if available_ns_configs is not None:
            o('Available Namespace configurations:')
            for ns_name in list_all():
                o('\t{}'.format(ns_name))
        else:
            o('No namespace configurations in deploy.yml')
    if r:
        o('Namespaces currently configured:')
        namespaces = get_all()
        for ns_data in namespaces['namespace']:
            o('\t{}'.format(ns_data['name']))
    if a:
        n = None
        available_ns_configs = list_all()
        if available_ns_configs is not None:
            add_all()
            o('Created all configured namespaces')
        else:
            o('No namespace configurations in deploy.yml')
    if n is not None:
        if namespace_exists(n):
            add_namespace(n)
            o('Created namespace {}'.format(n))
        else:
            o('No namespace named {}'.format(n))


@ecsconfig.command('bucket', short_help='Work with ECS Buckets')
@click.option('-l', is_flag=True, help='List known bucket configs')
@click.option('-r', is_flag=True, help='Get all current bucket configs from ECS')
@click.option('-s', default=None, help='Get current bucket configs from ECS for given namespace')
@click.option('-a', is_flag=True, help="Add all buckets to ECS")
@click.option('-n', default=None, help='Add the given bucket to ECS')
@pass_conf
def bucket(conf, l, r, s, a, n):
    """
    Work with ECS Buckets
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param r: list instances of this abstraction configured on ECS
    :param a: add all known configurations of this abstraction
    :param n: add a single known configuration of this abstraction
    :return: retval
    """
    def bucket_exists(bucket_name):
        if bucket_name in list_all():
            return True
        return False

    def add_bucket(bucket_name):
        bucket_opts = conf.ecs.get_bucket_options(bucket_name)
        bkt_create_dict = {
            'namespace': bucket_opts['namespace'],
            'replication_group': conf.get_rg_id_by_name(bucket_opts['replication_group']),
            'head_type': bucket_opts['head_type'],
            'filesystem_enabled': bucket_opts['filesystem_enabled'],
            'stale_allowed': bucket_opts['stale_allowed'],
            'encryption_enabled': bucket_opts['encryption_enabled']
        }
        bkt_owner = bucket_opts['owner']

        conf.api_client.bucket.create(bucket_name, **bkt_create_dict)
        conf.api_client.bucket.set_owner(bucket_name, bkt_owner, namespace=bucket_opts['namespace'])
        return True

    def list_all():
        return conf.ecs.get_bucket_names()

    def get_all():
        list_buckets = []
        for namespace in conf.ecs.get_ns_names():
            for bucket_list in get_all_in_namespace(namespace):
                list_buckets.append(bucket_list)
        return list_buckets

    def get_all_in_namespace(namespace_name):
        list_buckets = []
        for dict_info in conf.api_client.bucket.list(namespace_name)['object_bucket']:
            list_buckets.append(dict_info['id'])
        return list_buckets

    def add_all():
        for bucket_name in list_all():
            add_one(bucket_name)

    def add_one(bucket_name):
        conf.wait_for_dt_ready()
        o('Creating bucket: {}'.format(bucket_name))
        res = add_bucket(bucket_name)
        o('\tOK')
        return res

    if l:
        available_bucket_configs = list_all()
        if available_bucket_configs is not None:
            o('Available Bucket configurations:')
            for bucket_name in list_all():
                o('\t{}'.format(bucket_name))
        else:
            o('No bucket configurations in deploy.yml')
    if s:
        n = None
        o('Buckets currently configured in namespace "{}":'.format(s))
        buckets = get_all_in_namespace(s)
        if len(buckets) > 0:
            for bucket_id in buckets:
                o('\t{}'.format(bucket_id))
        if len(buckets) <= 0:
            o('No buckets configured in namespace "{}":'.format(s))
    if r:
        n = None
        o('Buckets currently configured:')
        buckets = get_all()
        if len(buckets) > 0:
            for bucket_id in buckets:
                o('\t{}'.format(bucket_id))
        if len(buckets) <= 0:
            o('No buckets configured.')
    if a:
        n = None
        available_bucket_configs = list_all()
        if available_bucket_configs is not None:
            o('Creating all buckets')
            add_all()
            o('Created all configured buckets')
        else:
            o('No bucket configurations in deploy.yml')
    if n is not None:
        if bucket_exists(n):
            o('Creating single bucket by name')
            add_one(n)
            o('Created bucket {}'.format(n))
        else:
            o('No bucket configuration named {} in deploy.yml'.format(n))


@ecsconfig.command('object-user', short_help='Work with ECS Object Users')
@click.option('-l', is_flag=True, help='List known object user configs')
@click.option('-r', is_flag=True, help='Get all current object user configs from ECS')
# @click.option('-s', default=None, help='Get current object user configs from ECS for given namespace')
@click.option('-a', is_flag=True, help="Add all object user to ECS")
@click.option('-n', default=None, help='Add the given object user to ECS')
@pass_conf
def object_user(conf, l, r, a, n):
    """
    Work with ECS Object Users
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param r: list instances of this abstraction configured on ECS
    :param s: list management users associated with given namespace
    :param a: add all known configurations of this abstraction
    :param n: add a single known configuration of this abstraction
    :return: retval
    """
    config_type = 'object user'

    def list_all():
        return conf.ecs.get_ou_names()

    def config_exists(name):
        if name in list_all():
            return True
        return False

    def get_all():
        list_return = []
        for dict_info in conf.api_client.object_user.list()['blobuser']:
            list_return.append(dict_info)
        return list_return

    def get_one(name):
        return conf.api_client.object_user.get(name)

    def add_all():
        o('Creating all {}s'.format(config_type))
        for this_name in list_all():
            add_one(this_name)

    def add_one(name):
        ou_namespace = conf.ecs.get_ou_namespace(name)
        ou_dict = conf.ecs.get_ou_dict(name)

        o("Creating '{}' in namespace '{}'".format(name, ou_namespace))
        conf.api_client.object_user.create(name, namespace=ou_namespace)

        o("\tWaiting for '{}' to become editable".format(name))
        is_editable = False
        while is_editable is False:
            try:
                get_one(name)
                is_editable = True
                o("\tOK")
            except Exception as e:
                is_editable = False
                o("\tWaiting...")
                time.sleep(5)

        creds_added = False
        while creds_added is False:
            try:
                o("\tAdding {}'s S3 credentials".format(name))
                conf.api_client.secret_key.create(user_id=name,
                                                  namespace=ou_namespace,
                                                  expiry_time=ou_dict['s3_expiry_time'],
                                                  secret_key=ou_dict['s3_secret_key'])
                creds_added = True
            except Exception as e:
                creds_added = False
                time.sleep(5)

        creds_added = False
        while creds_added is False:
            try:
                if ou_dict['swift_password'] is not None and ou_dict['swift_groups_list'] is not None:
                    o("\tAdding {}'s Swift credentials".format(name))
                    conf.api_client.password_group.create(user_id=name,
                                                          namespace=ou_namespace,
                                                          password=ou_dict['swift_password'],
                                                          groups_list=ou_dict['swift_groups_list'])
                creds_added = True
            except Exception as e:
                creds_added = False
                time.sleep()

    available_configs = list_all()
    if l:
        if available_configs is not None:
            o('Available {} configurations:'.format(config_type))
            for name in list_all():
                o('\t{}'.format(name))
        else:
            o('No {} configurations in deploy.yml'.format(config_type))
    if a:
        n = None
        if available_configs is not None:
            o('Creating all configured {}s:'.format(config_type))
            add_all()
            o('Created all configured {}s'.format(config_type))
        else:
            o('No {} configurations in deploy.yml'.format(config_type))
    if r:
        n = None
        items = get_all()
        o('All {} configured on ECS:'.format(config_type))
        for item in items:
            o("\t" + item)
    # if s is not None:
    #     n = None
    #     print(get_one(g))
    if n is not None:
        if config_exists(n):
            add_one(n)
            o('Created {} named {}'.format(config_type, n))
        else:
            o('No {}s named {}'.format(config_type, n))


@ecsconfig.command('management-user', short_help='Work with ECS Management Users')
@click.option('-l', is_flag=True, help='List known management user configs on Install Node')
@click.option('-r', is_flag=True, help='List current management users on ECS')
@click.option('-g', is_flag=False, help='Get management user info from ECS for given username')
# @click.option('-s', is_flag=False, help='Get current management user configs from ECS for given namespace')
@click.option('-a', is_flag=True, help="Add all management user to ECS")
@click.option('-n', default=None, help='Add the given management user to ECS')
@pass_conf
def management_user(conf, l, r, a, g, n):
    """
    Work with ECS Management Users
    """
    """
    Work with a collection of ECS abstractions
    :param conf: Click object containing the configuration
    :param l: list known configurations of this abstraction
    :param r: list instances of this abstraction configured on ECS
    :param s: list management users associated with given namespace
    :param a: add all known configurations of this abstraction
    :param n: add a single known configuration of this abstraction
    :return: retval
    """
    config_type = 'management user'

    def list_all():
        return conf.ecs.get_mu_names()

    def config_exists(name):
        if name in list_all():
            return True
        return False

    def get_all():
        list_return = []
        for dict_info in conf.api_client.management_user.list()['mgmt_user_info']:
            list_return.append(dict_info['userId'])
        return list_return

    def get_one(name):
        return conf.api_client.management_user.get(name)

    def add_all():
        for this_name in list_all():
            add_one(this_name)
            o('\t{}'.format(this_name))

    def add_one(name):
        mu_pass = conf.ecs.get_mu_password(name)
        mu_dict = conf.ecs.get_mu_dict(name)
        conf.api_client.management_user.create(name, password=mu_pass, **mu_dict)

    available_configs = list_all()

    if l:
        if available_configs is not None:
            o('Available {} configurations:'.format(config_type))
            for name in list_all():
                o('\t{}'.format(name))
        else:
            o('No {} configurations in deploy.yml'.format(config_type))
    if a:
        n = None
        if available_configs is not None:
            o('Creating all configured {}s:'.format(config_type))
            add_all()
            o('Created all configured {}s'.format(config_type))
        else:
            o('No {} configurations in deploy.yml'.format(config_type))
    if r:
        n = None
        items = get_all()
        o('All {} configured on ECS:'.format(config_type))
        for item in items:
            o("\t" + item)
    if g is not None:
        n = None
        print(get_one(g))
    if n is not None:
        if config_exists(n):
            add_one(n)
            o('Created {} named {}'.format(config_type, n))
        else:
            o('No {} named {}'.format(config_type, n))


if __name__ == '__main__':
    ecsconfig()
