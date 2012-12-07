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
    
    
    print api.Branches.get_count()
    for branch in api.Branches.enumerate():
        print branch.name, branch.id
        
        
        limit=0
        f = api.Invoices.filters()
        f["from"].set(datetime.now() - timedelta(days=2))
        if branch.name != "Head Office":
            f.branch_id.set(branch.id)
            limit=0
        
        
        for invoice in api.Invoices.enumerate(limit=limit, query=f):
            print invoice.id, invoice.amount
        
        """
        pf = api.Products.filters()
        if branch.name != "Head Office":
            pf.branch_id.set(branch.id)
            
        print "Products"
        for p in api.Products.enumerate(start=5, limit=20, query=pf):
            qty = p.inquire("quantity",pf)
            print "\t", p.id, p.name, qty
        """ 
    
        """
        print "Documents"
        df = api.Documents.filters()
        df["from"].set(datetime.now() - timedelta(days=15))
        if branch.name != "Head Office":
            df.branch_id.set(branch.id)
    
        print api.Documents.get_count(query=df)
        for product in api.Documents.enumerate(limit=10, query=df):
            print product.id
        """ 
        

    """
    
    # List 10 products starting at offset 10
    for invoice in api.Invoices.enumerate():
        print invoice.id, invoice.invoice_no, invoice.amount
        for line in invoice.invoice_lines:
            print "Line Items", line.product_id, line.price, line.quantity
        pass
    
    f = api.Documents.filters()
    f["from"].set(datetime.now() - timedelta(15))
    
    print api.Documents.get_count(query=f)
    for product in api.Documents.enumerate(query=f):
        print product.id
        
    doc = api.Documents.get(product.id)
    
    d = datetime.utcnow() - timedelta(days=20)
    
    print "Quantities Since", d
    f = api.Products.filters()
    f["from"].set(d)
    
    for product in api.Products.enumerate(query=f):
        quantity = product.inquire("quantity")
        print product.stock_no, product.name, quantity
        
    
    d = datetime.utcnow() - timedelta(minutes=20)
    print "Invoices Since", d
    f = api.Invoices.filters()
    f["from"].set(d)
    
    for invoice in api.Invoices.enumerate(query=f):
        print invoice.id, invoice.invoice_no, invoice.amount
        for line in invoice.invoice_lines:
            print "Line Items", line.product_id, line.price, line.quantity
        pass
    """
        
    