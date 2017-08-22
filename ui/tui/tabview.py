#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2013 Mountainstorm
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import urwid
import logging
import os
import sys
import dotmap
from constants import *

logging.basicConfig(filename=ui_log, level=logging.DEBUG)
logging.debug('-' * 40 + os.path.abspath(__file__) + '-' * 40)


class TabHandle(urwid.WidgetWrap):
    def __init__(self, tab_view, attr, title, closable=False):
        self.tab_view = tab_view
        self.title = title
        self.closable = closable
        display_label = u' ' + title + u' '
        # if closable:
        #     display_label += u'✕ '
        display_widget = urwid.Text((attr, display_label))
        urwid.WidgetWrap.__init__(self, display_widget)

    def set_attr(self, attr):
        self._w = urwid.Text((attr, self._w.get_text()[0]))

    # def mouse_event(self, size, event, button, col, row, focus):
    #     if button == 1:
    #         if self.closable:
    #             tab_width = self._w.pack(size)[0]
    #             if col == tab_width - 2:
    #                 # close this tab
    #                 self.tab_view._close_by_tab(self)
    #                 return
    #         # make this tab active
    #         self.tab_view._set_active_by_tab(self)
        # raise AttributeError("b: %s - c: %u, r: %u - ev: %s" % (button, col, row, event))


class TabView(urwid.WidgetWrap):
    def __init__(self, director, attr_active, attr_inactive, tabs, focus=None):
        self.attr_active = attr_active
        self.attr_inactive = attr_inactive
        self._contents = []
        self.director = director
        tab_bar = urwid.Columns([], 1)
        display_widget = urwid.Frame(
                urwid.AttrWrap(urwid.SolidFill(u' '), attr_active),
                header=tab_bar
        )
        urwid.WidgetWrap.__init__(self, display_widget)
        # now add all the tabs
        for tab in tabs:
            self.add_tab(tab)
        if focus is not None:
            self.set_active_tab(focus)

    def add_tab(self, tab):
        name, content, closable = tab[0], tab[1], False
        if len(tab) == 3:
            closable = tab[2]
        tab_bar = self._w.contents['header'][0]
        tab_bar.contents.append(
                (
                    TabHandle(
                            self,
                            self.attr_active,
                            name,
                            closable
                    ),
                    tab_bar.options('pack')
                )
        )
        self._contents.append(tab)
        self.set_active_tab(len(self._contents) - 1)

    def set_active_tab(self, idx):
        tab_bar = self._w.contents['header'][0]
        for i, tab in enumerate(tab_bar.contents):
            if i == idx:
                tab[0].set_attr(self.attr_active)
            else:
                tab[0].set_attr(self.attr_inactive)
        # set the view content to the tabs
        self._w.contents['body'] = (
            urwid.AttrWrap(
                    self._contents[idx][1],
                    self.attr_active
            ),
            self._w.contents['body'][1]
        )
        self.active_tab = idx

    def set_active_next(self):
        if self.active_tab < (len(self._contents) - 1):
            self.set_active_tab(self.active_tab + 1)

    def set_active_prev(self):
        if self.active_tab > 0:
            self.set_active_tab(self.active_tab - 1)

    def close_active_tab(self, force=False):
        tab_bar = self._w.contents['header'][0]
        if tab_bar.contents[self.active_tab][0].closable or force:
            del tab_bar.contents[self.active_tab]
            new_idx = self.active_tab
            if len(self._contents) <= self.active_tab:
                new_idx -= 1
            del self._contents[self.active_tab]
            self.set_active_tab(new_idx)

    def _set_active_by_tab(self, tab):
        tab_bar = self._w.contents['header'][0]
        for idx, t in enumerate(tab_bar.contents):
            if t[0] is tab:
                self.set_active_tab(idx)
                break

    def _close_by_tab(self, tab):
        tab_bar = self._w.contents['header'][0]
        for idx, t in enumerate(tab_bar.contents):
            if t[0] is tab:
                self.set_active_tab(idx)
                self.close_active_tab()
                break

    def close_tab_by_name(self, name, force=False):
        tab_bar = self._w.contents['header'][0]
        for idx, t in enumerate(tab_bar.contents):
            if name in t[0].title:
                self.set_active_tab(idx)
                self.close_active_tab(force)
                break
