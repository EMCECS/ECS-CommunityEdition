# author: deadc0de6
# contact: https://github.com/deadc0de6
#
# the gui
#
# Copyright (C) 2014 deadc0de6
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import urwid # python-urwid
import subprocess
import getpass
import datetime

class Entry(urwid.Text):
  def selectable(self):
      return True
  def keypress(self,  size,  key):
      return key

class ui():

  # this defines the color for the different elements
  # format: <keyword>, <font color>, <background color> <display attr>
  palette = [
      ('body','dark cyan', '', 'standout'),
      ('focus','dark red', '', 'standout'),
      ('head','light red', 'black'),
      ('north', 'dark cyan', '', 'standout'),
      ('south', 'yellow', ''),
      ]

  header_txt = 'Server monitor 0.2 (user: \'%s\') - by https://deadc0de6.github.io' % (getpass.getuser())
  footer_txt = ' | cmd: '
  empty_txt = [
    Entry('Please select an element above:'),
    Entry('   Enter:   select'),
    Entry('   r:       reload'),
    Entry('   up/down: navigate'),
    Entry('   j/k:     navigate'),
    Entry('   h:       display this help'),
    Entry('   q:       quit'),
  ]

  def __init__(self, up_entries, script_match):
    self.up_entries = up_entries
    self.script_match = script_match

    # the north panel
    self.north_entries = urwid.SimpleListWalker([urwid.AttrMap(w, None, 'body') for w in up_entries])
    self.northPanel = urwid.ListBox(self.north_entries)

    # the south panel
    self.content = urwid.SimpleListWalker(self.get_south_content(''))
    self.southPanel = urwid.ListBox(self.content)

    # the global content
    # LineBox add a surrounding box around the widget
    self.cont = urwid.Pile([('fixed', 10, urwid.LineBox(self.northPanel)), urwid.LineBox(self.southPanel),])
    # create the header
    header = urwid.AttrMap(urwid.Text(self.header_txt), 'head')
    footer = urwid.AttrMap(urwid.Text(self.get_date() + self.footer_txt), 'head')
    # create the global frame
    self.view = urwid.Frame(self.cont, header=header, footer=footer)
    # start the main loop
    loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke, handle_mouse=False)
    loop.run()

  def get_date(self):
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  def extexec(self, cmd):
    text = []
    if cmd == None or cmd == '':
      return ('', False)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
      if line == None:
        continue
      text.append(line.rstrip())
    ret = p.wait()
    return (text, ret)

  def get_south_content(self, cmd):
    if cmd == '':
      content = [urwid.AttrWrap(w, None, 'south') for w in self.empty_txt]
    else:
      (text, ret) = self.extexec(cmd)
      if text == '' or ret != 0:
        content = [urwid.AttrMap(w, None, 'south') for w in self.empty_txt]
      else:
        content = [urwid.AttrMap(Entry(w), None, 'south') for w in text]
    return content


  def set_header(self, txt):
    # update header
    self.view.set_header(urwid.AttrWrap(urwid.Text(
        self.header_txt + txt), 'head'))

  def set_footer(self, txt):
    # update footer
    self.view.set_footer(urwid.AttrWrap(urwid.Text(
        self.get_date() + self.footer_txt + txt), 'head'))

  def update_display(self):
    focus, pos = self.northPanel.get_focus()
    cmd = self.script_match.get(pos)
    if cmd == '':
      return
    self.set_header(' - item %s' % (str(self.up_entries[pos].get_text()[0])))
    self.set_footer('\"%s\"' % (cmd))
    # update south pane
    self.content[:] = self.get_south_content(cmd)

  # return True if focus is on north widget
  def get_focus_up(self):
    l = self.cont.widget_list
    idx = l.index(self.cont.focus_item)
    return idx == 0

  def set_focus(self, up):
    l = self.cont.widget_list
    if up:
      self.cont.set_focus(l[0])
    else:
      self.cont.set_focus(l[1])

  def inv_focus(self):
    up = self.get_focus_up()
    if up:
      self.set_focus(False)
    else:
      self.set_focus(True)

  def keystroke(self, input):
      if input in ('q', 'Q'):
          raise urwid.ExitMainLoop()

      if input is 'enter' or input is ' ':
        self.update_display()

      if input is 'r':
        self.update_display()

      if input is 'j':
        if self.get_focus_up():
          focus, pos = self.northPanel.get_focus()
          if pos >= len(self.north_entries)-1:
            return
          self.northPanel.set_focus(pos+1)
        else:
          focus, pos = self.southPanel.get_focus()
          if pos >= len(self.content)-1:
            return
          self.southPanel.set_focus(pos+1)

      if input is 'k':
        if self.get_focus_up():
          focus, pos = self.northPanel.get_focus()
          if pos == 0:
            return
          self.northPanel.set_focus(pos-1)
        else:
          focus, pos = self.southPanel.get_focus()
          if pos == 0:
            return
          self.southPanel.set_focus(pos-1)

      if input is 'h' or input is '?': # help
        self.content[:] = self.get_south_content('')

      if input is 'tab':
        self.inv_focus()

