# author: deadc0de6
# contact: https://github.com/deadc0de6
#
# class representing a plugin
#   - name
#   - menu entry
#   - cmd to execute
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

class plugin():
  '''
  @name: the plugin name
  @menu_txt: what will be displayed in the menu
  @cmd: command (shell one-liner) exected when menu selected
  '''
  def __init__(self, name, menu_txt, cmd):
    self.name = name
    self.menu_txt = menu_txt
    self.cmd = cmd

  def __repr__(self):
    return 'name: \"%s\", menu: \"%s\", cmd: \"%s\"' % (self.name, self.menu_txt, self.cmd)
