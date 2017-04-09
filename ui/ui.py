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

"""
#
"""
import logging
import os
import sys
import urwid
import tui

"""
# Logging
"""


logging.basicConfig(filename='/var/log/ui.log', level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


"""
# Classes that haven't been refactored into their own modules
"""

# Nothing at this time

"""
# Ostensibly Necessary Globals
"""

# Nothing at this time.


def main():
    """
    # Initial State
    """

    d = tui.Director(script_file='install_script.yml', init_tui=True)

    """
    # Mainloop
    """

    logging.debug(sys._getframe().f_code.co_name + ': ' + 'starting MainLoop')
    loop = urwid.MainLoop(d.run(), d.palette,
                          handle_mouse=True,
                          pop_ups=True,
                          unhandled_input=d.handle_unhandled_keys)

    loop.screen.set_terminal_properties(colors=256)
    # loop.screen.set_terminal_properties(colors=16)
    loop.screen.set_mouse_tracking()
    loop.run()


if __name__ == '__main__':
    main()
