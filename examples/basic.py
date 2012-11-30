STORE_HOST = "www.YOURHOST.com"
STORE_TOKEN = "YOUR_TOKEN"
STORE_USERID = "userid"
import xml.etree.ElementTree
from settings import *
import sys
import logging
from pprint import pprint
from Imonggo.api import ApiClient

logging.basicConfig(level=logging.DEBUG, 
                    stream=sys.stdout,
                    format='%(asctime)s %(levelname)-8s[%(name)s] %(message)s',
                    datefmt='%m/%d %H:%M:%S')
log = logging.getLogger("main")

if __name__ == "__main__":
    log.debug("HOST %s, USER: %s" % (STORE_HOST, STORE_USERID))
    api = ApiClient(STORE_HOST, STORE_TOKEN, STORE_USERID)
    
    print api.Invoices.get_count()
    
    # List 10 products starting at offset 10
    for invoice in api.Invoices.enumerate():
        print invoice.id, invoice.invoice_no, invoice.amount
        for line in invoice.invoice_lines:
            print "Line Items", line.product_id, line.price, line.quantity
        pass
    
    