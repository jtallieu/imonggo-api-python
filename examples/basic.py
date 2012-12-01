STORE_HOST = "www.YOURHOST.com"
STORE_TOKEN = "YOUR_TOKEN"
STORE_USERID = "userid"

from settings import *
import sys
import logging
from pprint import pprint
from datetime import datetime, timedelta
from Imonggo.api import ApiClient

logging.basicConfig(level=logging.INFO, 
                    stream=sys.stdout,
                    format='%(asctime)s %(levelname)-8s[%(name)s] %(message)s',
                    datefmt='%m/%d %H:%M:%S')
log = logging.getLogger("main")

if __name__ == "__main__":
    log.debug("HOST %s, USER: %s" % (STORE_HOST, STORE_USERID))
    api = ApiClient(STORE_HOST, STORE_TOKEN, STORE_USERID)
    
    
    
    
    
    # List 10 products starting at offset 10
    for invoice in api.Invoices.enumerate():
        print invoice.id, invoice.invoice_no, invoice.amount
        for line in invoice.invoice_lines:
            print "Line Items", line.product_id, line.price, line.quantity
        pass
    
    f = api.Documents.filters()
    f["from"].set(datetime.now() - timedelta(3))
    
    print api.Documents.get_count(query=f)
    for product in api.Documents.enumerate(query=f):
        print product.id
        
    doc = api.Documents.get(product.id)
    
    for product in api.Products.enumerate():
        if product.stock_no == "4":
            break
        
    print product.id, product.stock_no
        
    prod =  api.Products.get(product.id)
    print prod.inquire("quantity")