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
import tui
from tools import logobj
from constants import *

logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


class WidgetFactory(object):

    def __init__(self):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

    def create_widget(self, widget_blueprint):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if not widget_blueprint.type:
            raise ValueError("No widget type defined in blueprint")
        else:
            # TODO: Replace this with a proper mapping hash because using globals() is bad
            wobj = globals()[widget_blueprint.type]

        # TODO: refactor this later because it's ugly
        wdirector = widget_blueprint.director or None
        wargs = widget_blueprint.args or None
        wbody = widget_blueprint.body or None
        wbrief = widget_blueprint.brief or None
        wtitle = widget_blueprint.title or None
        wnamespace = widget_blueprint.namespace or None
        wkeytexts = widget_blueprint.keytexts or None

        logobj(wobj)
        logobj(wdirector)
        logobj(wargs)
        logobj(wbody)
        logobj(wbrief)
        logobj(wtitle)
        logobj(wnamespace)
        logobj(wkeytexts)

        # * 'args': [{'prev_button': 'EmptyWidget'}],
        # * 'body': 'Thank you etc etc.\n',
        #   'brief': 'Free and Frictionless Overview',
        #   'help': 'popup help Use the arrowkeys etc etc',
        # - 'keys': ['help', 'exit', 'color'],
        # * 'title': 'EMC ECS 2.2 Community Edition',
        # * 'type': 'InfoOverlay'}
        # * key_texts = "[F1] Help | [F5] Save etc etc"
        # * director = Director obj where callbacks can be made
        # * namespace = config file variable namespace
        #
        # What needs to be sent to an InfoOverlay,
        # title_widget urwid.Text(title_text, align='center')
        # nav_widget = widgets.NavButtonBox(self.d)
        # body_widget = urwid.Text(body)
        # bg_widget = widgets.TabBackground(header_text, footer_text, **kwargs)
        # logobj(widget_blueprint)
        nav_widget = NavButtonBox(wdirector, **wargs)
        logobj(nav_widget)

        title_widget = urwid.Text(wtitle, align='center')
        logobj(title_widget)

        # If wbody is none, then assume the constructor for
        # for the widget will take care of rendering its own body
        # from the provided args
        if wbody is not None:
            body_widget = urwid.Text(wbody)
        else:
            body_widget = wbody

        # TODO: bind popup widgets to this (for help, logs, etc)
        bg_widget = TabBackground(head_text=wbrief, foot_text=wkeytexts)

        # Pass everything on down to new object
        wdict = {'nav_widget': nav_widget,
                 'title_widget': title_widget,
                 'body_widget': body_widget,
                 'namespace': wnamespace,
                 'director': wdirector,
                 'bg_widget': bg_widget
                 }

        wdict.update(wargs)

        return wobj.__init(**wdict)


class InfoOverlay(urwid.Overlay):
    """
    Generic overlay page generator
    :param title: Overlay window title
    :param body: Overlay window body
    :param d: Main tab director object
    """
    def __init__(self, title_widget, body_widget, nav_widget, bg_widget, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)

        title = urwid.AttrWrap(title_widget, 'header')
        body = urwid.Padding(body_widget, left=5, right=5)

        content = [body]
        listboxframe = urwid.Frame(urwid.AttrWrap(urwid.ListBox(content), 'readme'), header=title)
        top = urwid.Pile([('weight', 10, listboxframe), (3, nav_widget)], focus_item=1)

        super(InfoOverlay, self).__init__(top, bg_widget, 'center', ('relative', 66), 'middle', ('relative', 66))


class StyledFrame(urwid.Frame):
    """
    Generates a Frame pre-wrapped in palette styles
    """
    def __init__(self, body, foot_text=None, head_text=None, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        logobj(foot_text)
        logobj(head_text)
        footer = urwid.Text(' ' + foot_text, align='center')
        footer = urwid.AttrWrap(footer, 'footer')
        header = urwid.Text(' ' + head_text, align='center')
        header = urwid.AttrWrap(header, 'header')
        urwid.Frame.__init__(self, body=body, footer=footer, header=header, **kwargs)


class TabBackground(StyledFrame):
    """
    Renders a background object with header and footer.
    :param header: text should usually be brief help
    :param footer: text should usually be hotkey text
    """
    def __init__(self, head_text=None, foot_text=None, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        logobj(foot_text)
        logobj(head_text)
        # Tab background
        body = urwid.AttrMap(urwid.SolidFill(fill_char=' '), 'bg')
        StyledFrame.__init__(self, StyledFrame(body=body, foot_text=foot_text, head_text=head_text, **kwargs), **kwargs)


class NavButtonBox(urwid.AttrWrap):
    """
    Box object for navigation buttons
    :param d: Primary tab director object
    :param prev_button: Optionally change the next and previous buttons
    :param next_button: to a different widget.
    """
    def __init__(self, d, prev_button=None, next_button=None):
        buttons = urwid.Padding(NavButtonBar(d, prev_button, next_button), align='right', left=5, right=5, width='pack')
        buttons = urwid.Filler(buttons, valign='middle', min_height=1, height='pack')
        urwid.AttrWrap.__init__(self, buttons, 'controls')


class NavButtonBar(urwid.Columns):
    """
    Flow object for navigation buttons
    :param d: Primary tab director object
    :param prev_button: Optionally change the next and previous buttons
    :param next_button: to a different widget.
    """
    def __init__(self, d, prev_button=None, next_button=None):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if prev_button is None:
            pb = PrevButton(d)
        else:
            pb = globals()[prev_button](d)

        if next_button is None:
            nb = NextButton(d)
        else:
            nb = globals()[next_button](d)

        div = urwid.Divider(div_char=' ')
        urwid.Columns.__init__(self, [div, pb, nb], focus_column=2, dividechars=5, min_width=7)


class EmptyWidget(urwid.Pile):
    """
    A blank nothing widget with zero height and width
    """
    def __init__(self, *args, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        urwid.Pile.__init__(self, [])


class CenterButton(urwid.AttrMap):
    """
    An auto-styled Urwid button with centered text.

    :param label: Button label
    :param on_press: Callback when button is clicked
    :param user_data: Additional data to send along to callback
    """

    def __init__(self, label='Button', on_press=None, user_data=None):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.label = label
        self.on_press = on_press
        self.user_data = user_data
        self.w = urwid.Button(label=self.label, on_press=self.on_press, user_data=self.user_data)
        self.w._label.align = 'center'
        urwid.AttrMap.__init__(self, self.w, attr_map='button', focus_map='button_focus')


class NextButton(CenterButton):
    """
    An auto-styled Urwid button with centered text for moving to next tab.

    :param d: A Director object
    """

    def __init__(self, d, *args, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        CenterButton.__init__(self, label='Next', on_press=d.forward)


class PrevButton(CenterButton):
    """
    An auto-styled Urwid button with centered text for moving to previous tab.

    :param d: A Director object
    """

    def __init__(self, d, *args, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        CenterButton.__init__(self, label='Prev', on_press=d.backward)


class NextSet(CenterButton):
    """
    An auto-styled Urwid button with centered text for moving to next set in the setlist.
    :param d: A Director object
    """

    def __init__(self, d, *args, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        CenterButton.__init__(self, label='Next Step', on_press=d.next_step)


class PrevSet(CenterButton):
    """
    An auto-styled Urwid button with centered text for moving to previous set in the setlist.
    :param d: A Director object
    """

    def __init__(self, d, *args, **kwargs):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        CenterButton.__init__(self, label='Next Step', on_press=d.prev_step)


"""
urwid.BaseScreen.register_palette_entry(
                                        name,
                                        foreground, background,
                                        mono=None,
                                        foreground_high=None, background_high=None
                                        )

    Register a single palette entry.

    name – new entry/attribute name

    foreground – a string containing a comma-separated foreground color and settings

        Color values: ‘default’ (use the terminal’s default foreground), ‘black’, ‘dark red’, ‘dark green’, ‘brown’,
        ‘dark blue’, ‘dark magenta’, ‘dark cyan’, ‘light gray’, ‘dark gray’, ‘light red’, ‘light green’, ‘yellow’,
        ‘light blue’, ‘light magenta’, ‘light cyan’, ‘white’

        Settings: ‘bold’, ‘underline’, ‘blink’, ‘standout’

        Some terminals use ‘bold’ for bright colors. Most terminals ignore the ‘blink’ setting. If the color is not
        given then ‘default’ will be assumed.

    background – a string containing the background color

        Background color values: ‘default’ (use the terminal’s default background), ‘black’, ‘dark red’,
        ‘dark green’, ‘brown’, ‘dark blue’, ‘dark magenta’, ‘dark cyan’, ‘light gray’

    mono – a comma-separated string containing monochrome terminal settings (see “Settings” above.)

        None = no terminal settings (same as ‘default’)

    foreground_high – a string containing a comma-separated foreground color and settings, standard foreground colors
    (see “Color values” above) or high-colors may be used

        High-color example values: ‘#009’ (0% red, 0% green, 60% red, like HTML colors) ‘#fcc’ (100% red, 80% green,
        80% blue) ‘g40’ (40% gray, decimal), ‘g#cc’ (80% gray, hex), ‘#000’, ‘g0’, ‘g#00’ (black), ‘#fff’, ‘g100’,
        ‘g#ff’ (white) ‘h8’ (color number 8), ‘h255’ (color number 255)

        None = use foreground parameter value

    background_high – a string containing the background color, standard background colors (see “Background colors”
    above) or high-colors (see “High-color example values” above) may be used

        None = use background parameter value
"""

# modified from urwid/examples/edit.py
#
# Urwid example lazy text editor suitable for tabbed and format=flowed text
#    Copyright (C) 2004-2009  Ian Ward
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: http://excess.org/urwid/

"""
Urwid lazy text viewer suitable for tabbed and flowing text

Features:
- custom list walker for lazily loading text file
- includes buttons for accepting or rejecting the license

Usage:
EulaWalker(<file>, accept_callback)

"""


class LicenseWalker(urwid.ListWalker):
    """ListWalker-compatible class for lazily reading file contents."""

    def __init__(self, name, d):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.filesize = os.path.getsize(name)
        self.file = open(name, 'r')
        self.lines = []
        self.focus = 0
        self.bytesread = 0
        self.position = 0
        self.d = d
        if not d.license_accepted:
            self.footer = urwid.ProgressBar('progress_normal', 'progress_complete',
                                            current=self.bytesread, done=self.filesize,
                                            satt=None)
        self.btn_accept = CenterButton('Accept', on_press=self.continue_installer)
        self.btn_accept = urwid.AttrMap(self.btn_accept, 'button', focus_map='button_focus')
        self.btn_exit = CenterButton('Cancel', on_press=self.exit_installer)
        self.btn_exit = urwid.AttrMap(self.btn_exit, 'button', focus_map='button_focus')
        self.divider = urwid.AttrWrap(urwid.Divider(div_char=' '), 'readme')

    def exit_installer(self, button):
        """
        Button callback for rejecting license and exiting script
        :param button: Button callback boilerplate
        :raises: urwid.ExitMainLoop()
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        raise urwid.ExitMainLoop()

    def continue_installer(self, button):
        """
        Button callback for accepting and continuing script
        :param button: Button callback boilerplate
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.d.license_accepted = True
        bin = self.lines.pop()
        bin = self.lines.pop()
        self.lines.append(self.divider)
        self.lines.append(NavButtonBar(self.d))
        self.d.accept_license()

    def get_focus(self):
        # logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        return self._get_at_pos(self.focus)

    def set_focus(self, focus):
        # logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        self.focus = focus
        self._modified()

    def get_next(self, start_from):
        # logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        return self._get_at_pos(start_from + 1)

    def get_prev(self, start_from):
        # logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        return self._get_at_pos(start_from - 1)

    def read_next_line(self):
        # logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        """Read another line from the file."""

        next_line = self.file.readline()

        if not next_line or next_line[-1:] != '\n':
            # no newline on last line of file
            self.file = None
            self.bytesread += self.filesize
            if not self.d.license_accepted:
                buttons = urwid.Columns([self.btn_accept, self.divider, self.btn_exit])
                self.lines.append(urwid.Divider(div_char=' '))
                self.lines.append(urwid.AttrWrap(buttons, 'button'))
                self.lines.append(urwid.Divider(div_char=' '))
        else:
            # trim newline characters
            next_line = next_line[:-1]
            self.bytesread += len(next_line)
            expanded = next_line.expandtabs()
            text = urwid.Text(expanded, align='left')
            text.original_text = next_line
            self.lines.append(text)

        if not self.d.license_accepted:
            self.footer.set_completion(self.bytesread)

        return next_line

    def _get_at_pos(self, pos):
        # logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        """Return a widget for the line number passed."""

        if pos < 0:
            # line 0 is the start of the file, no more above
            self.position = 0
            return None, None

        if len(self.lines) > pos:
            # we have that line so return it
            self.position = pos
            return self.lines[pos], pos

        if self.file is None:
            # file is closed, so there are no more lines
            return None, None

        assert pos == len(self.lines), "out of order request?"

        self.read_next_line()

        return self.lines[-1], pos


class LicenseConfirm(urwid.Overlay):
    def __init__(self, name, d):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        topw = self.render_body(name, d)
        bottomw = self.render_background(d)
        super(LicenseConfirm, self).__init__(topw, bottomw, 'center',
                                             ('relative', 66), 'middle',
                                             ('relative', 66))

    def render_header(self):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        header = urwid.Text(('banner', ' License Agreement '), align='center')
        return urwid.AttrWrap(header, 'banner')

    def render_body(self, name, d):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        header = self.render_header()
        walker = LicenseWalker(name, d)

        if d.license_accepted:
            footer = None
        else:
            footer = walker.footer

        listbox = urwid.ListBox(walker)
        listbox_wrapped = urwid.AttrWrap(urwid.Padding(
                urwid.AttrWrap(listbox, 'readme'),
                align='center', left=5, right=5,
        ), 'readme')
        body = urwid.Frame(listbox_wrapped, header=header, footer=footer)
        return body

    def render_background(self, d):
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        t = tui.TuiConfig()
        if d.license_accepted:
            return t.render_background(head_text='You have accepted the license')
        else:
            return t.render_background(head_text='License must be accepted to proceed')

#
# END modified from urwid/examples/edit.py
#
