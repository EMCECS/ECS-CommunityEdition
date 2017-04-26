#!/usr/bin/python
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


class SplitViewDivider(urwid.WidgetWrap):
    def __init__(self, horiz, attr=None):
        self._horiz = horiz

        urwid.WidgetWrap.__init__(self, divide)


class SplitView(urwid.WidgetWrap):
    def __init__(self, first, second, horiz, split=0.5, attr=None, divide=None):
        self._horiz = horiz
        self._indrag = None
        self._split = split
        if horiz:
            if divide is None:
                divide = u'─'
            divide = urwid.AttrWrap(urwid.SolidFill(divide), attr)
        else:
            if divide is None:
                divide = u'│'
            divide = urwid.AttrWrap(urwid.SolidFill(divide), attr)

        contents = [
            (u'weight', split, first),
            (1, divide),
            (u'weight', 1.0 - split, second)
        ]
        if horiz:
            cont = urwid.Pile(contents)
        else:
            cont = urwid.Columns(contents, min_width=0)
        urwid.WidgetWrap.__init__(self, cont)

    def mouse_event(self, size, event, button, col, row, focus):
        retval = True
        if (event == u'mouse press'
            and button == 1
            and self._inside_div(size, col, row, focus)):
            self._indrag = (col, row)  #  start drag
        elif self._indrag and event == u'mouse release':
            self._indrag = None  # end drag
        elif self._indrag and event == u'mouse drag':
            delta = col - self._indrag[0]
            if self._horiz:
                delta = row - self._indrag[1]
            if delta != 0:
                # we've actually moved - re-calculate the split
                if self._split > 0.0 and self._split < 1.0:
                    #  only update if we adjusted - otherwise it all feels wrong
                    self._indrag = (col, row)
                self._update_split(size, delta, focus)
        else:
            retval = self._w.mouse_event(size, event, button, col, row, focus)
        return retval

    def _inside_div(self, size, col, row, focus):
        retval = False
        if self._horiz:
            rows = self._w.get_item_rows(size, focus)[0]
            if row == rows:
                retval = True
        else:
            cols = self._w.column_widths(size, focus)[0]
            if col == cols:
                retval = True
        return retval

    def _update_split(self, size, delta, focus):
        if self._horiz:
            s = size[1]
        else:
            s = size[0]
        self._split += (1.0 / s) * delta
        self._split = max(min(self._split, 1.0), 0.0)
        options = self._w.options(u'weight', self._split)
        self._w.contents[0] = (self._w.contents[0][0], options)
        options = self._w.options(u'weight', 1.0 - self._split)
        self._w.contents[2] = (self._w.contents[2][0], options)
