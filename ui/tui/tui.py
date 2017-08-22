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
from tools import DataSet
from tools import logobj
from constants import *

logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


class KeyBind(object):
    """
    Represents a bound key
    """
    def __init__(self, name, key, call, text, active=False):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.name = name
        self.key = key
        self.call = call
        self.text = text
        self.active = active

    def activate(self):
        """
        Activates the keybind
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.active = True

    def deactivate(self):
        """
        Deactivates the keybind
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.active = False

    def press(self):
        """
        Calls self.call when invoked if the keybind is active
        :returns: True, always, even if inactive because Urwid
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if self.active:
            self.call()
            return True
        else:
            return True

    def get_text(self):
        """
        Returns the key text
        :return: text describing the key suitable for helpframe
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        return self.text



class TuiConfig(object):
    """
    A collection of tools for the TUI
    """

    config_file = None
    config_content = None
    config = None

    def __init__(self):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

    def roundwebcolor(self, hexrgb):
        """
        Converts six-digit hex color to three-digit hex color (with rounding) for 16bit colors
        that need to be translated into 8bit terminals (ie. Urwid)

        :param hexrgb a typical six-digit web color spec (eg. #FE5E74)
        :returns a three-digit web color spec (eg. #F56)
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        hexrgb = hexrgb.lstrip('#')
        hexlist = list(int(hexrgb[i: i + 6 / 3], 16) / 16 for i in range(0, 6, 2))
        hexdef = ''.join('%x' % i for i in hexlist).lower()
        return '#' + hexdef

    def render_palette(self):
        """
        Generates a palette for the TUI. As much as possible keeps EMC brand colors.

        :returns A palette tuple set compatible with urwid.BaseScreen.register_palette()
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        emc_blue = self.roundwebcolor('#2C95DD')
        emc_gray = self.roundwebcolor('#BABCBE')

        colorconfig = [
            (
                'header',
                'white, bold', 'light blue',
                'standout',
                'white, bold', emc_blue
             ),
            # (
            #     'footer',
            #     'dark gray', 'black',
            #     '',
            #     'g11', 'black'
            # ),
            ('footer', 'header'),
            (
                'panel',
                'light gray', 'light blue',
                '',
                emc_gray, emc_blue
             ),
            (
                'focus',
                'white', 'dark gray',
                'standout',
                'white', 'dark gray'
            ),
            (
                'bg',
                'dark gray', 'black',
                '',
                'g11', 'g7'
            ),
            (
                'banner',
                'dark blue', 'white',
                '',
                'dark blue', 'white'
            ),
            (
                'streak',
                'light blue', 'dark gray',
                '',
                emc_blue, 'g7'
            ),
            ('readme', 'focus'),
            ('controls', 'focus'),
            ('button_focus', 'banner'),
            ('button', 'streak'),
            ('tab_inactive', 'streak'),
            ('tab_active', 'banner'),
            (
                'progress_normal',
                'white', 'dark gray',
                'standout',
                'white', 'dark gray'
            ),
            (
                'progress_complete',
                'white', 'light blue',
                '',
                'white', emc_blue
            ),
            (
                'progress_smooth',
                'light blue', 'dark gray',
                '',
                emc_blue, 'dark gray'
            )
        ]
        return colorconfig



