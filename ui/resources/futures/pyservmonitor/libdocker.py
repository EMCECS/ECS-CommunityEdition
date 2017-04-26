# author: deadc0de6
# contact: https://github.com/deadc0de6
#
# docker library
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
# https://docs.docker.com/reference/api/docker_remote_api_v1.10/
# https://docs.docker.com/reference/api/docker_remote_api_v1.15/
#
# TODO
# find docker socket with python
#
# basic usage
#r = dockerapi()
#r.DEBUG = True
#r.connect()
#print r.get_docker_version()
#print r.get_docker_info()
#print r.get_images_info()
#print r.get_containers_info()
#print r.get_conts_details()
#print r.get_conts_log()
#r.disconnect()

import socket
import sys
import json
from httplib import HTTPConnection # sudo apt-get install python-httplib2

# http lib for unix sockets
class dockhttp(HTTPConnection):

  def __init__(self, path):
    HTTPConnection.__init__(self, '127.0.0.1')
    self.path = path

  # overwrite connect method with unix socket
  def connect(self):
    self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    self.sock.connect(self.path)

class dockerapi():
  # netstat --protocol=unix | grep docker | awk '{print $8}'
  DEFADDR = '/var/run/docker.sock'
  DEBUG = False

  ERR_NONE = '2'
  ERR_NO_SUCH_CONTAINER = '4'
  ERR_SERVER_ERROR = '5'

  # docker requests
  REQ_DOCKER_INFO = '/info'
  REQ_DOCKER_VERSION = '/version'

  # container requests
  REQ_CONT_LIST_RUNNING = '/containers/json?all=0&size=1'
  REQ_CONT_LIST_ALL = '/containers/json?all=1&size=1'
  REQ_CONT_INSPECT = '/containers/%s/json' # container-id
  REQ_CONT_LIST_PROCESS = '/containers/%s/top' # container-id
  REQ_CONT_LOG = '/containers/%s/logs?stderr=1&stdout=1&timestamps=1&follow=0&tail=all' # container-id

  # image requests
  REQ_IMG_LIST_NOTALL = '/images/json?all=0'
  REQ_IMG_LIST_ALL = '/images/json?all=1'
  REQ_IMG_INSPECT = '/images/%s/json' # image-name
  REQ_IMG_HISTORY = '/images/%s/history' # image-name

  def __init__(self):
    pass

  def connect(self, addr=DEFADDR):
    self._http = dockhttp(addr)
    self._http.set_debuglevel(0)

  def disconnect(self):
    self._http.close()

  def get_cont_ids(self):
    return [d['Id'] for d in self.query(self.REQ_CONT_LIST_RUNNING)]

  def get_cont_details(self, cont_id):
    return self._to_string(self.query(self.REQ_CONT_INSPECT % (cont_id)))

  def strip_bash_char(self, string):
    res = string.replace('[?1034h', '')
    res = res.replace('[K', '\n')
    res = res.replace('\x1b', '')
    return res

  def get_cont_log(self, cont_id):
    dummy = self.query(self.REQ_CONT_LOG %
      (cont_id), jsondata=False)
    return self.strip_bash_char(dummy)

  def get_conts_details(self):
    ret = ''
    for i in self.get_cont_ids():
      ret += self.get_cont_details(i) + '\n'
    return ret

  def get_conts_log(self):
    ret = ''
    for i in self.get_cont_ids():
      ret += self.get_cont_log(i) + '\n'
    return ret

  # as string
  def get_docker_version(self):
    return self._to_string(self.query(self.REQ_DOCKER_VERSION))

  # as string
  def get_docker_info(self):
    # docker info in dict
    #res = self.query(self.REQ_DOCKER_INFO)
    #print res
    return self._to_string(self.query(self.REQ_DOCKER_INFO))

  # as string
  def get_images_info(self):
    return self._to_string(self.query(self.REQ_IMG_LIST_NOTALL))

  # as string
  def get_containers_info(self):
    return self._to_string(self.query(self.REQ_CONT_LIST_ALL))

  def query(self, req, jsondata=True):
    try:
      self._debug('requesting: %s' % (req))
      self._http.request('GET', req)
      resp = self._http.getresponse()
      err = self._parse_status(str(resp.status))
      if err != '':
        self._debug('error: %s' % (err))
        return err
      content = resp.read()
      if jsondata:
        data = json.loads(content)
      else:
        data = content
      return data
    except socket.error as err:
      if err.errno == 2:
        self._error('socket file not found')
      else:
        self._error('Errno: %i' % (err.errno))
      return None

  def _to_string(self, stuff):
    return json.dumps(stuff, sort_keys=True, indent=4, separators=(',', ': '))

  def _parse_status(self, status):
    if status.startswith(self.ERR_NONE):
      return ''
    if status.startswith(self.ERR_NO_SUCH_CONTAINER):
      return 'no such container'
    if status.startswith(self.ERR_SERVER_ERROR):
      return 'server error'
    return 'unknown error (%s)' % (status)

  def _error(self, string):
    sys.stderr.write('[ERROR] %s\n' % (string))

  def _debug(self, string):
    if not self.DEBUG:
      return
    sys.stderr.write('[DEBUG] %s\n' % (string))

