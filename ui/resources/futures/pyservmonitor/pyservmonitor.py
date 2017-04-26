#!/usr/bin/python
# author: deadc0de6
# contact: https://github.com/deadc0de6
#
# server monitorer frontend
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
# deps:
#   urwid (python-urwid in debian)

import plugin
from cfg_reader import cfg_reader
import argparse
from ui import *
import os
import sys

def err(string):
  sys.stderr.write(string+'\n')

def out(string):
  sys.stdout.write(string+'\n')

parser = argparse.ArgumentParser(description='server manager frontend')
parser.add_argument('--config', required=False, default='config.ini', help='the config file')
args = parser.parse_args()
cfg = args.config

# check user is root
#if os.geteuid() != 0:
#  err('get r00t !')
#  sys.exit(0)

if not os.path.isfile(cfg) or not os.path.exists(cfg):
  err('config file \"%s\" does not exist !' % (cfg))
  sys.exit(1)

cfgr = cfg_reader(cfg)
plugins = cfgr.get_plugins()
err('%i entries parsed from config \"%s\"' % (len(plugins), cfg))

# Let's construct the lists for the ui
# - up_entries: the menu entry
# - script_match: the commands
up_entries = []
script_match = {}
for i,p in enumerate(plugins):
  up_entries.append(Entry('%i) %s' % (i+1, p.menu_txt)))
  script_match[i] = p.cmd

ui(up_entries, script_match)

