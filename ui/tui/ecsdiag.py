"""
Module for querying ECS diagnostic service
"""

import requests
from xml.etree import ElementTree
from constants import *


class ECSDiag(object):
    """
    A class to query the diagnostic service
    """

    def __init__(self, endpoint):
        self.address = endpoint
        self.endpoint = '{0}://{1}:{2}'.format(DIAGNOSTIC_PROTOCOL, endpoint, DIAGNOSTIC_PORT)

    def get_dt_status(self):
        """
        Query diag service for Data Table statuses
        """
        status_dict = {}
        try:
            dt_xml = requests.get('{0}/stats/dt/DTInitStat/'.format(self.endpoint))
            etree = ElementTree.fromstring(dt_xml.text)
            for entry in etree.findall("./entry//"):
                status_dict.update({entry.tag: int(entry.text)})

        except Exception as e:
            status_dict.update({'unready_dt_num': 0, 'unknown_dt_num': -1})

        status_dict.update({'endpoint': self.address})

        return status_dict
