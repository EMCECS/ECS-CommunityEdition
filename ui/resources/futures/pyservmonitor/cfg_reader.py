# author: deadc0de6
# contact: https://github.com/deadc0de6
#
# the config file reader
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
# format:
#   <name>:<menu-entry>:<command>

import re
import csv
from plugin import plugin

class cfg_reader():
  DEBUG = False

  def __init__(self, path):
    self._path = path
    self._plugins = []
    self._parse()

  def _parse(self):
    with open(self._path, 'r') as f:
      reader = csv.reader(f, delimiter=':', quoting=csv.QUOTE_MINIMAL, quotechar='\'', escapechar='\\')
      for row in reader:
        self._parse_line(row)

  def _parse_line(self, fields):
    if self.DEBUG:
      print 'parsing %s ...' % (fields)
    if len(fields) != 3:
      if self.DEBUG:
        print 'line %s too few elemtns' % (fields)
      return
    if fields[0][0] == '#':
      if self.DEBUG:
        print 'line %s is a comment' % (fields)
      return

    name = fields[0]
    entry = fields[1]
    cmd = fields[2]

    if self.DEBUG:
      print 'adding: %s' % (fields)
    self._plugins.append(plugin(name, entry, cmd))

  def get_plugins(self):
    return self._plugins

