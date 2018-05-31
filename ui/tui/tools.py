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
import yaml
import jinja2
import sys
import os
import click
from constants import *

logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


def logobj(obj):
    logging.debug('=' * 20 + obj.__class__.__name__ + '=' * 20)
    logging.debug(repr(obj))
    logging.debug('=' * 20 + obj.__class__.__name__ + '=' * 20)


class DataSet(object):
    """
    Reads, writes, and renders data sets with Jinja2 templating and single recursion.
    :param data_file: File to load
    :param create_if_missing: Create an empty config if the file is missing
    """
    def __init__(self, data_file, create_if_missing=False, additional_template_yaml=None,
                 additional_template_vars=None):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        # Store the filename so we can "save" later.
        self.data_file = data_file

        try:
            # Slurp the yemplate file (as utf-8)
            yemplate = self.slurp_file(self.data_file).decode('utf-8')

            # Read whatever vars we can from the YAML and then pass it through jinja2
            # as both a template and the vars for the template. This gives us our
            # one level of recursion.

            # Try rendering current shared configs into template file
            try:
                if additional_template_vars is not None:
                    yemplate = self.render_template(yemplate, template_vars=additional_template_vars)
            except jinja2.UndefinedError as e:
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
                pass

            # Mix in other yaml for alias resolution
            if additional_template_yaml is not None:
                yemplate = additional_template_yaml + yemplate

            # Render the file as yaml and store a dict
            template_dict = self.render_yaml(yemplate)

            # Import any additional vars for the template
            if additional_template_vars is not None:
                template_dict.update(additional_template_vars)

            # Store the resulting yaml so we can use it in other loads
            self.yaml = self.render_template(yemplate, template_vars=template_dict)

            # Render the merged yaml and store the resulting dict.
            self.content = self.render_yaml(self.yaml)

        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            if create_if_missing:
                self.content = {}
                self.write_config()
            else:
                # Welp.
                raise

        except jinja2.exceptions.UndefinedError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            print('Jinja2 template error in file: {0}'.format(repr(e)))
            sys.exit(1)

    def slurp_file(self, data_file):
        """
        Read the configuration into memory for future processing.
        :param data_file: A YAML file containing data
        :return: String of file contents if successful
        :raises: IOError if unsuccessful
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + data_file)
        try:
            with open(data_file, 'r') as fp:
                return str(fp.read())
        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            raise

    def render_yaml(self, yam):
        """
        Renders a yaml string into Python objects
        :param yam: A string of YAML
        :return: a pyyaml object
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        return yaml.load(yam)

    def render_template(self, template, template_vars=None, **kwargs):
        """
        Renders a Jinja2 template using vars passed in as a dict-like object
        :param template: A Jinja2 template object
        :param template_vars: a dict- or list-like object full of vars to pass to Jinja2 template
        :return:
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        tpl = jinja2.Template(template)

        return tpl.render(template_vars, **kwargs)

    def save(self):
        """
        alias for write_config
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.write_config()

    def write_config(self):
        """
        Writes the current config to yaml
        :return: True of successful
        :raises: IOError if unsuccessful
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        try:
            with open(self.data_file, 'w') as fp:
                # Make yaml human-friendly by forcing block style
                fp.write(yaml.dump(self.content, default_flow_style=False))
                return True
        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            # bigger fish to fry
            raise


class JinjaCopy(DataSet):
    """
    Copies a file from src to dst after passing through Jinja2 with vars in data arg
    """
    def __init__(self, src, dst, data):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        try:
            raw_file = self.slurp_file(src).decode('utf-8')
            cooked_file = self.render_template(raw_file, template_vars=data)
            self.write_file(dst, cooked_file)

        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            raise

    def write_file(self, dst, cooked_file):
        """
        Writes the the ostensibly rendered templated file out to its destination
        :return: True of successful
        :raises: IOError if unsuccessful
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        try:
            with open(dst, 'w') as fp:
                fp.write(cooked_file)
                return True
        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            # bigger fish to fry
            raise


class DumpFacts(DataSet):
    """
    Dumps the facts key to a yaml file, presumably to transform deploy.yml into ansible group_vars/all
    """
    def __init__(self, src, dst):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        try:
            raw_file = self.slurp_file(src).decode('utf-8')
            vardict = self.render_yaml(raw_file)
            self.write_file(dst, yaml.dump(vardict.get('facts'), default_flow_style=False))

        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            raise

    def write_file(self, dst, cooked_file):
        """
        Writes the the ostensibly rendered templated file out to its destination
        :return: True of successful
        :raises: IOError if unsuccessful
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        try:
            with open(dst, 'w') as fp:
                fp.write(cooked_file)
                return True
        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            # bigger fish to fry
            raise


def o(message, nl=True):
    """
    Generic unified output function
    :param message: string message to output
    :param nl: bool trailing newline
    :return:
    """
    click.echo('> {}'.format(message))


def die(message, exception=None):
    """
    Generic unified output and exit(1) function
    :param message: see o()
    :param exception: the exception to output
    :return:
    """
    o("FATAL: {}".format(message))
    o(exception)
    sys.exit(1)
