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
import platform


class ScrollArea(urwid.Widget):
    _sizing = frozenset([u'box'])

    signals = [u'modified', u'scrolled']

    def __init__(self, w):
        self.content = w
        self._xscroll = 0
        self._yscroll = 0
        self._xlimit = 0
        self._ylimit = 0
        self._xratio = 0.0
        self._yratio = 0.0
        self.xlocation = 0.0
        self.ylocation = 0.0

    def rows(self, size, focus=False):
        return size

    def render(self, size, focus=False):
        (maxcol, maxrow) = size
        col = maxcol
        if u'fixed' in self.content.sizing():
            (col, row) = self.content.pack((), focus)
            canvas = self.content.render((), focus)
        elif u'flow' in self.content.sizing():
            row = self.content.rows((maxcol,))
            canvas = self.content.render((maxcol,), focus)
        else:
            raise TypeError('ScrollArea content must be fixed, or flow sized')

        ratiox = min(float(maxcol) / col, 1.0)
        ratioy = min(float(maxrow) / row, 1.0)
        if ratiox != self._xratio or ratioy != self._yratio:
            self._xratio = ratiox
            self._yratio = ratioy
            self._emit(u'modified', (ratiox, ratioy))

        self._xlimit = max(col - maxcol, 0)
        self._ylimit = max(row - maxrow, 0)

        comp = urwid.CompositeCanvas(canvas)
        deltay = maxrow - row
        deltax = maxcol - col
        comp.pad_trim_top_bottom(-self._yscroll, deltay + self._yscroll)
        comp.pad_trim_left_right(-self._xscroll, deltax + self._xscroll)
        return comp

    def keypress(self, areax, areay, key):
        # TODO: translate coordinates?
        # (areax, areay) = self._get_area_size(size)
        if u'keypress' in dir(self.content):
            self.content.keypress(areax, areay, key)

    def mouse_event(self, size, event, button, col, row, focus):
        # TODO: translate coordinates?
        if u'mouse_event' in dir(self.content):
            self.content.mouse_event(size, event, button, col, row, focus)

    def get_cursor_coords(self, size):
        # TODO: translate coordinates?
        if u'get_cursor_coords' in dir(self.content):
            self.content.get_cursor_coords(size)

    def get_pref_col(self, size):
        # TODO: translate coordinates?
        if u'get_pref_col' in dir(self.content):
            self.content.get_pref_col(size)

    def move_cursor_to_coords(self, size, col, row):
        # TODO: translate coordinates?
        if u'move_cursor_to_coords' in dir(self.content):
            self.content.move_cursor_to_coords(size, col, row)

    def scroll_vertical(self, yloc):
        """Moves the viewable area so that the yloc part.  yloc is a value
		between 0.0 and 1.0, where 0.0 will show the start of the content at the
		begining of the view, and 1.0 will show the end of the content at the
		end of the view"""
        if yloc >= 0.0 and yloc <= 1.0:
            # calculate actual location based on yloc
            self._yscroll = int(float(self._ylimit) * yloc)
            self._invalidate()
            self._update_location()

    def scroll_horizontal(self, xloc):
        """Moves the viewable area so that the xloc part. xloc is a value
		between 0.0 and 1.0, where 0.0 will show the start of the content at the
		left of the view, and 1.0 will show the end of the content at the
		right of the view"""
        if xloc >= 0.0 and xloc <= 1.0:
            # calculate actual location based on xloc
            self._xscroll = int(float(self._xlimit) * xloc)
            self._invalidate()
            self._update_location()

    def scroll_vertical_step(self, step):
        """Scrolls the view up or down by step rows, +iv scrolls down, -ive
		scrolls up"""
        y = self._yscroll - step
        if y < 0:
            y = 0
        elif y > self._ylimit:
            y = self._ylimit
        self._yscroll = y
        self._invalidate()
        self._update_location()

    def scroll_horizontal_step(self, step):
        """Scrolls the view left or right by step cols, +iv scrolls right, -ive
		scrolls left"""
        x = self._xscroll - step
        if x < 0:
            x = 0
        elif x > self._xlimit:
            x = self._xlimit
        self._xscroll = x
        self._invalidate()
        self._update_location()

    def _update_location(self):
        self.xlocation = 0.0 if self._xlimit == 0 else float(self._xscroll) / self._xlimit
        self.ylocation = 0.0 if self._ylimit == 0 else float(self._yscroll) / self._ylimit
        self._emit(u'scrolled', (self.xlocation, self.ylocation))


class ScrollBar(urwid.Widget):
    _sizing = frozenset([u'fixed'])
    _selectable = True

    signals = [u'scroll']

    def __init__(self, attr=None, fill=u'█'):
        self.size = 0.0  # not normally known until its 1st rendered
        self.location = 0.0
        self._attr = attr
        self._fill = fill
        self._dragstart = None

    def set_size(self, size):
        self.size = size
        self._invalidate()

    def set_location(self, location):
        self.location = location
        self._invalidate()

    def _mouse_event(self, size, event, button, location):
        # event and location are both just the relavent axis
        barsize = int((self.size * size) + 0.5)
        pad = size - barsize
        barstart = int((float(pad) * self.location) + 0.5)
        retval = False
        if button == 1:
            if event == u'mouse press':
                if location < barstart:
                    # Note: both these bar click events should really do this,
                    # but I think I prefer the current behavious
                    # self.location = max(
                    #	min(
                    #		float(barstart + barsize) / size,
                    #		1.0),
                    #	0.0)
                    self.location -= (float(barsize) / size)
                    self.location = max(self.location, 0.0)
                    self._invalidate()
                    self._emit(u'scroll', self.location)
                    retval = True
                elif location >= (barstart + barsize):
                    self.location += (float(barsize) / size)
                    self.location = min(self.location, 1.0)
                    self._invalidate()
                    self._emit(u'scroll', self.location)
                    retval = True
                else:
                    self._dragstart = location
            elif event == u'mouse release':
                self._dragstart = None
            elif event == u'mouse drag':
                # if location >= barstart and location < (barstart + barsize):
                if self._dragstart is not None:
                    step = location - self._dragstart
                    if step != 0:
                        self._dragstart = location

                        barstart += step
                        pad = size - int((self.size * size) + 0.5)
                        if pad != 0:
                            self.location = max(min(float(barstart) / pad, 1.0), 0.0)
                            self._invalidate()
                            self._emit(u'scroll', self.location)
                    retval = True
        return retval


class HScrollBar(ScrollBar):
    def __init__(self, attr=None, fill=u'━'):
        ScrollBar.__init__(self, attr, fill)

    def pack(self, size, focus=False):
        return (size[0], 1)

    def render(self, size, focus=False):
        (maxcol, maxrow) = size
        cols = int((self.size * maxcol) + 0.5)
        comp = urwid.CompositeCanvas(
                urwid.SolidCanvas(
                        self._fill,
                        cols,
                        maxrow
                )
        )
        pad = maxcol - cols
        leftpad = int((float(pad) * self.location) + 0.5)
        rightpad = pad - leftpad
        comp.pad_trim_left_right(leftpad, rightpad)
        comp.fill_attr(self._attr)
        return comp

    def mouse_event(self, size, event, button, col, row, focus):
        return ScrollBar._mouse_event(self, size[0], event, button, col)


class VScrollBar(ScrollBar):
    def __init__(self, attr=None, fill=u'┃'):
        ScrollBar.__init__(self, attr, fill)

    def pack(self, size, focus=False):
        return (1, size[0])

    def render(self, size, focus=False):
        (maxcol, maxrow) = size
        rows = int((self.size * maxrow) + 0.5)
        comp = urwid.CompositeCanvas(
                urwid.SolidCanvas(
                        self._fill,
                        maxcol,
                        rows
                )
        )
        pad = maxrow - rows
        toppad = int((float(pad) * self.location) + 0.5)
        bottompad = pad - toppad
        comp.pad_trim_top_bottom(toppad, bottompad)
        comp.fill_attr(self._attr)
        return comp

    def mouse_event(self, size, event, button, col, row, focus):
        return ScrollBar._mouse_event(self, size[1], event, button, row)


# BUG: dont let bar length go below 1
class ScrollView(urwid.Widget):
    _sizing = frozenset([u'box'])
    _selectable = True

    def __init__(self, w, attr=None):
        self._area = ScrollArea(w)
        self._hscroll = HScrollBar(attr)
        self._vscroll = VScrollBar(attr)
        self._inscroll = None
        self._corner = urwid.CompositeCanvas(
                urwid.TextCanvas(u' '.encode(u'utf-8'))
        )
        self._corner.fill_attr(attr)
        # connect up the signals between the area and scrollbar
        urwid.connect_signal(
                self._area,
                u'modified',
                self._scroll_area_modified
        )
        urwid.connect_signal(self._hscroll, u'scroll', self._scroll_by_bar)
        urwid.connect_signal(self._vscroll, u'scroll', self._scroll_by_bar)
        # calculate scroll dir - on OSX 10.8 its reversed
        self._scrolldelta = 1
        if platform.mac_ver()[0].startswith('10.'):
            if int(platform.mac_ver()[0].split('.')[1]) >= 8:
                self._scrolldelta = -1

    def _scroll_area_modified(self, sender, ratios):
        self._hscroll.set_size(ratios[0])
        self._vscroll.set_size(ratios[1])

    def _scroll_by_bar(self, sender, newloc):
        if sender == self._hscroll:
            self._area.scroll_horizontal(newloc)
        elif sender == self._vscroll:
            self._area.scroll_vertical(newloc)

    def rows(self, size, focus=False):
        return size

    def render(self, size, focus=False):
        (areax, areay) = self._get_area_size(size)
        area = self._area.render((areax, areay), focus)
        # join the lot together top to bottom, left to right
        vscroll_width = self._vscroll.pack(size)[0]
        hscroll_height = self._hscroll.pack(size)[1]
        col1 = urwid.CanvasCombine([
            (area, None, False),
            (self._hscroll.render((areax, hscroll_height)), None, False)
        ])
        col2 = urwid.CanvasCombine([
            (self._vscroll.render((vscroll_width, areay)), None, False),
            (self._corner, None, False)
        ])
        return urwid.CanvasJoin([
            (col1, None, False, areax),
            (col2, None, False, vscroll_width)
        ])

    def keypress(self, size, key):
        (areax, areay) = self._get_area_size(size)
        if key == u'home':
            self._area.scroll_vertical(0.0)
        elif key == u'end':
            self._area.scroll_vertical(1.0)
        elif key == u'page up':
            self._area.scroll_vertical_step(areay)
        elif key == u'page down':
            self._area.scroll_vertical_step(-areay)
        else:
            return self._area.keypress(self, areax, areay, key)

    def mouse_event(self, size, event, button, col, row, focus):
        retval = False
        if button == 4:  # up
            self._area.scroll_vertical_step(-self._scrolldelta)
            self._vscroll.set_location(self._area.ylocation)
            retval = True
        elif button == 5:  # down
            self._area.scroll_vertical_step(self._scrolldelta)
            self._vscroll.set_location(self._area.ylocation)
            retval = True
        else:
            (areax, areay) = self._get_area_size(size)
            # TODO: this needs tidying to remove the duplication
            if self._inscroll is not None:
                if event == u'mouse release':
                    self._inscroll = None
                if self._inscroll is self._vscroll:
                    retval = self._vscroll.mouse_event(
                            (areax, areay),
                            event,
                            button,
                            col - areax,
                            row,
                            focus
                    )
                elif self._inscroll is self._hscroll:
                    retval = self._hscroll.mouse_event(
                            (areax, areay),
                            event,
                            button,
                            col,
                            row - areay,
                            focus
                    )
            else:
                if col >= areax and row < areay:
                    if button == 1 and event == u'mouse press':
                        self._inscroll = self._vscroll
                    retval = self._vscroll.mouse_event(
                            (areax, areay),
                            event,
                            button,
                            col - areax,
                            row,
                            focus
                    )
                elif col < areax and row >= areay:
                    if button == 1 and event == u'mouse press':
                        self._inscroll = self._hscroll
                    retval = self._hscroll.mouse_event(
                            (areax, areay),
                            event,
                            button,
                            col,
                            row - areay,
                            focus
                    )
                else:
                    self._area.mouse_event(size, event, button, col, row, focus)
        return retval

    def get_cursor_coords(self, size):
        return self._area.get_cursor_coords(self._get_area_size(size))

    def get_pref_col(self, size):
        return self._area.get_pref_col(self._get_area_size(size))

    def move_cursor_to_coords(self, size, col, row):
        vscroll_width = self._vscroll.pack(size)[0]
        hscroll_height = self._hscroll.pack(size)[1]
        col -= vscroll_width
        row -= hscroll_height
        return self._area.move_cursor_to_coords(self._get_area_size(size), col, row)

    def _get_area_size(self, size):
        (maxcol, maxrow) = size
        vscroll_width = self._vscroll.pack(size)[0]
        hscroll_height = self._hscroll.pack(size)[1]
        areax = maxcol - vscroll_width
        areay = maxrow - hscroll_height
        return (areax, areay)
