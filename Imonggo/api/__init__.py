import os
import sys
import base64
import logging

from Imonggo.api.lib.connection import Connection
from resources import ResourceAccessor

log = logging.getLogger("Imonggo.api")


class ApiClient(object):
    BASE_URL = '/api/'
    
    def __init__(self, host, token, user_id):
        auth = base64.b64encode("%s:%s" % (token,user_id))
        self._connection = Connection(host, self.BASE_URL, auth)
        
        
    def connection(self):
        pass
    
    def get_url_registry(self):
        return self._connection.meta_data()
        
    def __getattr__(self, attrname):
        try:
            return ResourceAccessor(attrname, self._connection)
        except:
            raise AttributeError
        raise AttributeError
            