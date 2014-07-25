"""
Connection Module

Handles put and get operations to the a REST API
"""
import sys
import time
import urllib
import logging
import simplejson
from datetime import datetime
from urlparse import urlparse
from pprint import pprint, pformat
from StringIO import StringIO
from httplib import HTTPSConnection, HTTPException

from xml.sax import parse, parseString
from xml.sax.handler import ContentHandler
from xml.sax import SAXParseException

import xml.etree.cElementTree as ET
 
log = logging.getLogger("Imonggo.con")

class EmptyResponseWarning(HTTPException):
    pass

class DictToXML(object):
    
    def __init__(self, date_format="%Y-%m-%dT%H:%M:%sZ"):
        self.date_fmt = date_format
    
    def get_node(self, name, data):
        node = ET.Element(name)
        if isinstance(data, (basestring, int, float)):
            node.text = str(data)
            return node
        
        if isinstance(data, datetime):
            node.text = data.strftime(self.date_fmt)
            return node
        
        elif isinstance(data, list):
            node.set("type", "array")
            _name = name[0:-1]
            for o in data:
                _node = self.get_node(_name, o)
                node.append(_node)
                
        elif isinstance(data, dict):
            for key, value in data.items():
                node.append(self.get_node(key,value))
                
        return node
    
    
    def toxml(self, root_name = "", properties={}):
        root = ET.Element(root_name)
        for key, value in properties.items():
            n = self.get_node(key, value)
            root.append(n)
        return root
    
    
def toXML(rootname, properties):
    transformer = DictToXML()
    root = transformer.toxml(rootname, properties)
    buf = StringIO()
    ET.ElementTree(root).write(buf, xml_declaration=False)
    x = buf.getvalue()
    buf.close()
    return x
    
    
    

class DetailsToDict(ContentHandler):
    def __init__(self):
        self.data = {}
        self.stack = [['root',{}, "", False]]
        self.currentChars = ""
        
        
    def reduce(self, name=""):
        current = self.stack.pop()
        
        last = self.stack[-1]
        
        node_name = current[0]
        value = current[1] if len(current[1]) else current[2]
        
        # An array type is being closed
        if last[3]:
            
            if isinstance(value, list):
                last[1] += value
            elif isinstance(value, dict):
                last[1].append(value)
            
        else:
        
            if last[1].has_key(node_name):
                parent = last[1][node_name]
                if isinstance(parent,list):
                    parent.append(value)
                elif isinstance(parent,dict):
                    last[1][name] = [parent, value]
                else:
                    print 'unhandled event %s' % type(parent)
            else:
                last[1][node_name] = value
                
    def startElement(self, name, attrs):
        isarray = False
        if "type" in attrs.getNames():
            if attrs.getValue("type") == "array":
                isarray = True
                
        if isarray:
            self.stack.append([name,[],"", isarray])
        else:
            self.stack.append([name,{},"", isarray])
        
    def characters(self,content):
        last = self.stack[-1]
        last[2] = last[2] + content
    
    def endElement(self,name):
        self.reduce(name)
    
    def endDocument(self):
        
        last = self.stack.pop()
        self.data = last[1].values()[0] if len(last[1]) else last[2]
            
        if len(self.stack):
            print "%d items in the stack" % len(self.stack)
        
        
        
class Connection():
    """
    Connection class manages the connection to the REST API.
    """
    
    def __init__(self, host, base_url, auth):
        """
        Constructor
        
        On creation, an initial call is made to load the mappings of resources to URLS
        """
        self.host = host
        self.base_url = base_url
        self.auth = auth
        
        log.info("API Host: %s/%s" % (self.host, self.base_url))
        log.debug("Accepting json, auth: Basic %s" % self.auth)
        self.__headers = {"Authorization": "Basic %s" % self.auth,
                        "Accept": "application/xml"}
        
        self.__resource_meta = {}
        self.__connection = HTTPSConnection(self.host)
        
        
        
    def meta_data(self):
        """
        Return a string representation of resource-to-url mappings 
        """
        return simplejson.dumps(self.__resource_meta)    
        
        
    
    def get(self, url="", query={}):
        """
        Perform the GET request and return the parsed results
        """
        qs = urllib.urlencode(query)
        if qs:
            qs = "?%s" % qs
            
        url = "%s%s%s" % (self.base_url, url, qs)
        log.debug("GET %s" % (url))
        
        retries = 1
        last_code = 503
        result = {}
        delay = 90
        
        while retries < 5 and last_code == 503:
            self.__connection.connect()
            request = self.__connection.request("GET", url, None, self.__headers)
            response = self.__connection.getresponse()
            data = response.read()
            self.__connection.close()
            
            log.debug("GET %s status %d" % (url,response.status))
            log.debug('Response headers:')
            log.debug(pformat(response.getheaders()))
            result = {}
            last_code = response.status
            
            # Check the return status
            if response.status == 200:
                log.debug("%s" % data)
                parser = DetailsToDict()
                parseString(data, parser)
                return parser.data
                
            elif response.status == 204:
                raise EmptyResponseWarning("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
            
            elif response.status == 503:
                # Wait a minute
                log.critical("Max API call rate exceeded - waiting %ds [try %d]" % (retries * delay, retries))
                time.sleep(retries * delay)
                retries += 1
                
            elif response.status == 404:
                log.debug("%s returned 404 status" % url)
                raise HTTPException("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
            
            elif response.status >= 400:
                _result = simplejson.loads(data)
                log.debug("OUTPUT %s" % _result)
                raise HTTPException("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
            
        return result
        
    
    def get_url(self, resource_name):
        """
        Lookup the "url" for the resource name from the internally stored resource mappings
        """
        return self.__resource_meta.get(resource_name,{}).get("url", None)
    
    def get_resource_url(self, resource_name):
        """
        Lookup the "resource" for the resource name from the internally stored resource mappings
        """
        return self.__resource_meta.get(resource_name,{}).get("resource", None)
        
        
    def update(self, url, updates, resource_name=""):
        """
        Make a PUT request to save updates
        """
        url = "%s%s.xml" % (self.base_url, url)
        log.debug("PUT %s" % (url))
        self.__connection.connect()
        
        put_headers = {"Content-Type": "application/xml"}
        put_headers.update(self.__headers)
        log.debug("Call headers %s" % pformat(put_headers))
        payload = toXML(resource_name, updates)
        log.debug("Updating %s -> %s" % (resource_name, payload))
        request = self.__connection.request("PUT", url, payload, put_headers)
        response = self.__connection.getresponse()
        data = response.read()
        self.__connection.close()
        
        log.debug("PUT %s status %d" % (url,response.status))
        log.debug("OUTPUT: %s" % data)
        
        result = {}
        if response.status == 200:
            result = True
        
        elif response.status == 204:
            raise EmptyResponseWarning("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
        
        elif response.status == 404:
            log.debug("%s returned 404 status" % url)
            raise HTTPException("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
        
        elif response.status >= 400:
            _result = simplejson.loads(data)
            log.debug("OUTPUT %s" % _result)
            raise HTTPException("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
        
        return result
    
    
    def create(self, url, properties, name=""):
        resource_name = url if not name else name
        url = "%s%s.xml" % (self.base_url, url)
        log.debug("POST %s" % (url))
        log.debug("Creating %s" % pformat(properties))
        self.__connection.connect()
        
        put_headers = {"Content-Type": "application/xml"}
        put_headers.update(self.__headers)
        
        payload = toXML(resource_name, properties)
        log.debug("Creating %s -> %s" % (resource_name, payload))
        request = self.__connection.request("POST", url, payload, put_headers)
        response = self.__connection.getresponse()
        data = response.read()
        self.__connection.close()
        
        log.debug("POST %s status %d" % (url,response.status))
        log.debug("OUTPUT: %s" % data)
        
        result = {}
        if response.status == 201:
            parser = DetailsToDict()
            parseString(data, parser)
            return parser.data
        
        elif response.status == 204:
            raise EmptyResponseWarning("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
        
        elif response.status == 404:
            log.debug("%s returned 404 status" % url)
            raise HTTPException("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
        
        elif response.status >= 400:
            _result = simplejson.loads(data)
            log.debug("OUTPUT %s" % _result)
            raise HTTPException("%d %s @ https://%s%s" % (response.status, response.reason, self.host, url))
        
            
    
    def __repr__(self):
        return "Connection %s" % (self.host)
    
    


    