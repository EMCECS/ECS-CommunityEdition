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
import sys
import urwid
from dotmap import DotMap
import widgets
from tabview import TabView
from tools import DataSet, logobj
from tui import KeyBind, TuiConfig
from constants import *
from pprint import pprint
import pykwalify
from pykwalify.core import Core
from pykwalify.errors import SchemaError, CoreError

logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


class Director(object):
    """
    Directs traffic and tabs
    """


    # Defaults
    config_file = os.path.join(ui_etc, 'config.yml')
    caches_file = os.path.join(ui_etc, 'caches.yml')
    autonames_file = os.path.join(ui_etc, 'autonames.yml')
    schema_file = os.path.join(ui_etc, 'schema.yml')
    schema_functions_file = os.path.join(ui_tui, "schema_functions.py")
    deploy_file_host = os.path.join(host_root, 'deploy.yml')

    # state_file = '{0}/state.yml'.format(cache_root)
    state_file = None
    script_file = None
    deploy_file = None

    # TUI config, install script, state dicts and shortcuts
    tui_config = None
    config_dataset = None
    script_dataset = None
    state_dataset = None
    deploy_dataset = None

    template_vars = {}

    config = None
    script = None
    state = None
    deploy = None
    # state.step holds current deployment step
    # state.tab holds current tab within the step
    # state.license_accepted holds the obvious

    # Keybinds
    hotkeys = None

    # TabView
    tabs = None
    current_tab = None

    def __init__(self, config_file=None, script_file=None, state_file=None, deploy_file=None, init_tui=False):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        if config_file is not None:
            self.config_file = config_file

        if script_file is not None:
            self.script_file = '{0}/{1}'.format(ui_etc, script_file)

        if state_file is not None:
            self.state_file = state_file

        if deploy_file is not None:
            self.deploy_file = deploy_file

        self.load_config()

        if init_tui is True:
            self.tui_config = TuiConfig()
            self.palette = self.tui_config.render_palette()

        if self.script_file is not None:
            self.load_script()

        if self.state_file is not None:
            self.load_state()

        if self.deploy_file is not None:
            try:
                self.validate_deploy()
            except RuntimeError as e:
                print(e.msg)
                sys.exit(1)
            self.load_deploy()

        if self.script_file is not None:
            self.bind_hotkeys()
            self.validate_script_step()

    def load_state(self):
        """
        Load current state (may be empty)
        :raises IOError: if filesystem exceptions prevent config file read or initial write
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if self.state_file is None:
            pass
        else:

            try:
                self.update_template_vars()
                self.state_dataset = DataSet(self.state_file,
                                             additional_template_vars=self.template_vars)
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
                logobj(self.state_dataset.content)
                self.state = DotMap(self.state_dataset.content)
                logobj(self.state)
                self.update_template_vars()
            except IOError as e:
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
                # must be a new install or else we don't have permissions.
                # Try to create an empty config and see what happens.
                try:
                    self.state_dataset = DataSet(self.state_file, create_if_missing=True,
                                                 additional_template_vars=self.template_vars)
                    logobj(self.state_dataset.content)
                    self.state = DotMap(self.state_dataset.content)
                    logobj(self.state)
                    self.update_template_vars()
                except IOError as cf:
                    logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(cf))
                    print("Unable to create a new state file: " + repr(cf))
                    # and presumably crash, though at some point we should tell
                    # the user to make sure they're mounting /opt correctly in Docker
                    raise

    def load_config(self):
        """
        Loads the config
        :raises IOError: if can't read config
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        try:
            self.update_template_vars()
            self.config_dataset = DataSet(self.config_file)
            self.config = DotMap(self.config_dataset.content)
            logobj(self.config)
            self.update_template_vars()
        except IOError as e:
            # If this fails, there's nothing more we can do.
            # Something is broken in the install container.
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            print("Unable to locate config file: " + repr(e))
            raise

        if len(self.config.ui.script_file) != 0:
            self.script_file = self.config.ui.script_file
            logging.debug(self.__class__.__name__ + ': ' +
                          sys._getframe().f_code.co_name +
                          ': will look for script in: ' + repr(self.script_file))

        if len(self.config.ui.state_file) != 0:
            self.state_file = self.config.ui.state_file
            logging.debug(self.__class__.__name__ + ': ' +
                          sys._getframe().f_code.co_name +
                          ': will look for state in: ' + repr(self.state_file))

        if len(self.config.ui.deploy_file) != 0:
            self.deploy_file = self.config.ui.deploy_file
            logging.debug(self.__class__.__name__ + ': ' +
                          sys._getframe().f_code.co_name +
                          ': will look for deploy in: ' + repr(self.deploy_file))

    def load_script(self):
        """
        Loads the install script
        :raises IOError: if can't read script
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if self.script_file is None:
            pass
        else:
            try:
                self.update_template_vars()
                self.script_dataset = DataSet(self.script_file, additional_template_vars=self.config.toDict(),
                                              additional_template_yaml=self.config.yaml)
                self.script = DotMap(self.script_dataset.content)
                self.update_template_vars()
            except IOError as e:
                # If this fails, there's nothing more we can do.
                # Something is broken in the install container.
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
                print("Unable to locate script: " + repr(e))
                raise

    def validate_deploy(self):
        """
        Validates the deployment yaml file with the schema
        :raises pykwalify.errors.SchemaError: if validation fails
        :raises pykwalify.errors.CoreError: for other type of errors
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if not self.deploy_file:
            raise AssertionError

        try:
            c = Core(source_file=self.deploy_file,
                     schema_files=[self.schema_file],
                     extensions=[self.schema_functions_file])
            c.validate()
        except CoreError as e:
            # Most probably there is something wrong with the source files
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + e.msg)
            raise
        except SchemaError as e:
            # The deploy file is not valid
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + e.msg)
            print("The deployment file at '%s' is not valid." % (self.deploy_file_host,))
            raise

    def load_deploy(self):
        """
        Loads the deployment map
        :raises IOError: if can't read map
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if not self.deploy_file:
            raise AssertionError

        try:
            self.update_template_vars()
            self.deploy_dataset = DataSet(self.deploy_file,
                                          additional_template_vars=self.template_vars)
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
            logobj(self.deploy_dataset.content)
            self.deploy = DotMap(self.deploy_dataset.content)
            logobj(self.deploy)
            self.update_template_vars()

        except IOError as e:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
            # must be a new install or else we don't have permissions.

        autonames_dataset = DataSet(self.autonames_file, additional_template_vars=self.template_vars)
        autonames = DotMap(autonames_dataset.content)
        self.config.update(autonames)

        caches_dataset = DataSet(self.caches_file, additional_template_vars=self.template_vars)
        caches = DotMap(caches_dataset.content)
        self.config.update(caches)

    def update_template_vars(self):
        """
        update template vars with new data
        :return: null
        """
        if self.config is not None:
            self.template_vars.update(self.config.toDict())
        if self.deploy is not None:
            self.template_vars.update(self.deploy.toDict())
        if self.state is not None:
            self.template_vars.update(self.state.toDict())
        if self.script is not None:
            self.template_vars.update(self.script.toDict())

    def reset_config_step(self):
        """
        Resets config to a known if it's not populated or broken.
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.state.step = 0
        self.save()

    def validate_script_step(self):
        """
        Makes sure we have an operational setlist
        :return: True or False
        :raises ValueError:
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        # Where are we? Previous engagement?
        if self.state.state:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': state.state')
            if not self.state.state.step and not self.state.state.step == 0:
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': !state.state.step')
                self.reset_config_step()
                return True
            elif self.state.state.step > len(self.script.setlist) - 1 or self.state.state.step < 0:
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': OOB state.state.step')
                self.reset_config_step()
                return True
            else:
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': OK state.state.step')
                return True
        elif not self.state.state:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': !state.state')
            self.reset_config_step()
            return True
        else:
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': wtf')
            # also wtf
            raise ValueError('Unexpected config state, delete config and start over.')

    def bind_hotkeys(self):
        """
        Creates keybind objects in self
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.hotkeys = {}
        # do keys
        for key, keyconf in self.script.hotkeys.iteritems():
            logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name +
                          ': keybind: ' + repr(key) + ':' + repr(keyconf))
            self.hotkeys[key] = KeyBind(key, keyconf.key, keyconf.call, keyconf.text)

    def reconfigure_hotkeys(self, keylist):
        """
        Reconfigures keybinds, activating keys in keylist and deactivating all others.
        :param keylist: list of keys to activate
        :return: pipe | separated string of hotkey quick-help texts
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        keytexts = []
        for hotkey, obj in self.hotkeys.iteritems():
            if obj.name in keylist:
                obj.activate()
                keytexts.append(obj.text)
            else:
                obj.deactivate()
        keytexts = " | ".join(map(str, keytexts))
        return keytexts

    def play_setlist(self, start_at=0):
        """
        Plays the setlist to the screen
        :param start_at: Set in setlist to start playing
        :returns: A complete TabView widget
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        # We should eventually be returning an object
        namespace = self.script.setlist[start_at].keys()[0]
        tabset = self.script.setlist[start_at].get(namespace)

        return self.play_set(namespace, tabset)

    def play_set(self, namespace, tabset):
        """
        :param namespace: namespace for input values from this tabset saved in this deployment config
        :param tabset: tabset config DotMap
        :return: A complete TabView widget
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        # Reconfigure hotkeys and get keytexts
        # For now we're just going to turn them all on
        # TODO: Fix this so it's per-tab
        # keylist = []
        # for name, hotkey in self.hotkeys:
        #     keylist.append(hotkey.name)
        keytexts = self.reconfigure_hotkeys(self.hotkeys.keys())

        # Build tabs
        factory = widgets.WidgetFactory()
        tabview_tabs = []
        for blueprint in tabset:
            blueprint['namespace'] = namespace
            blueprint['keytexts'] = keytexts
            blueprint['director'] = self
            # logobj(blueprint)
            tabview_tabs.append(([blueprint['name'], factory.create_widget(DotMap(blueprint)), False]))

        # Build TabView
        return TabView(self, 'tab_active', 'tab_inactive', tabview_tabs, focus=0)

    def save(self):
        """
        shortcut to doing the juggling for writing the deployment config
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.state_dataset.content = self.state.toDict()
        self.state_dataset.save()

    def add_tab(self, newtab):
        """
        Adds a tab to the TabView
        :param newtab: a tuple of ('name', widget_object, boolClosable)
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.tabs.add_tab(newtab)

    def del_tab(self, tabname):
        """
        Deletes a tab from the TabView (semi-dangerous)
        :param tabname: String name of the tab to close
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.tabs.close_tab_by_name(tabname, force=True)

    def accept_license(self, button=None):
        """
        Called when the "Accept" button of a LicenseConfirm widget instance
        is selected. Used only once.
        Rearranges tabs to continue the installer process.
        :param button: Button widget boilerplate
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.state.state.license_accepted = True
        self.save()
        self.next_step()
        # self.add_tab(('Environment', page1, False))
        # self.del_tab('Overview')
        # self.forward()

    def forward(self, button=None):
        """
        Flips to the next tab to the right
        :param button: Button widget boilerplate
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.tabs.set_active_next()

    def backward(self, button=None):
        """
        Flips to the previous tab on the left
        :param button: Button widget boilerplate
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.save()
        self.tabs.set_active_prev()

    def next_step(self, button=None):
        pass

    def prev_step(self, button=None):
        pass

    def add_fake(self):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.save()
        self.add_tab(('fake', None, False))

    def del_fake(self):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.del_tab('fake')

    def run(self):
        """
        Starts the director
        :return: initial widget object for urwid mainloop
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.tabs = self.play_setlist(self.state.state.step)
        return self.tabs

        # Why do we zero index? http://exple.tive.org/blarg/2013/10/22/citation-needed/

    def handle_unhandled_keys(self, key):
        """
        Global function to handle otherwise unhandled keypresses.
        :param key: keypress key
        :raises: Main loop exit (quits the Urwid loop, not necessarily other loops)
        :returns: Always True
        """
        # Keypress
        # logging.debug(sys._getframe().f_code.co_name + ': unhandled: ' + repr(type(key)) + ' ' + str(key))
        if not isinstance(key, tuple):
            if key is u'ctrl x':
                logging.debug(sys._getframe().f_code.co_name + ': handled_key: ' + repr(key))
                raise urwid.ExitMainLoop()
            if key in ('right',):
                logging.debug(sys._getframe().f_code.co_name + ': handled_key: ' + str(key))
                self.forward()
                return True
            if key in ('left',):
                logging.debug(sys._getframe().f_code.co_name + ': handled_key: ' + str(key))
                self.backward()
                return True
            else:
                logging.debug(sys._getframe().f_code.co_name + ': unhandled: ' + repr(type(key)) + ' ' + str(key))
                return True
        # Must be a mouse action
        elif isinstance(key, tuple):
            logging.debug(sys._getframe().f_code.co_name + ': mouse: ' + str(key))
            return True
        #     action, button, x, y = key
        #     if action is 'mouse press':
        #         if button is 4:
        else:
            logging.debug(sys._getframe().f_code.co_name + ': unhandled: ' + repr(type(key)) + ' ' + str(key))
            return True
