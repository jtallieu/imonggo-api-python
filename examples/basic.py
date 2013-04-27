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
pos_log = logging.getLogger("pos")


def get_product_qty_adjustment(api, since):
    prods = {}
    product_ids = []
    branch_ids = []

    # Collect the branch id's
    pos_log.info("Getting Branches")
    for branch in api.Branches.enumerate():
        if branch.name != "Head Office":
            pos_log.info("Branch %s (%s)" % (branch.name, branch.id))
            branch_ids.append(branch.id)
    
    # Collect the product id's modified by each branch
    for branch_id in branch_ids:
        pos_log.info("Finding Inventory Documents for branch (%s) since %s" % (branch_id, since))
        f = api.Documents.filters()
        f["from"].set(since)
        f.branch_id.set(branch_id)
        logging.getLogger("Imonggo.con").setLevel(logging.DEBUG)
        for document in api.Documents.enumerate(query=f):
            for line in document.document_lines:
                pos_log.info("Product (%s) %s" % (line.product_stock_no, line.product_name))
                if not prods.has_key(line.product_id):
                    prods[line.product_id] = {"counted": False, "sold": False, "updated": False, "received": False}
                
                if document.document_type_code == "physical_count":
                    prods[line.product_id]["counted"] = True
                else:
                    prods[line.product_id]["received"] = True
                
        
        logging.getLogger("Imonggo.con").setLevel(logging.INFO)
        pos_log.info("Finding Invoices for branch (%s) since %s" % (branch_id, since))
        f = api.Invoices.filters()
        f["from"].set(since)
        pos_log.info("Finding invoices since since %s" % since)
        for invoice in api.Invoices.enumerate(query=f):
            for line in invoice.invoice_lines:
                pos_log.info("Product (%s) %s" % (line.product_stock_no, line.product_name))
                if not prods.has_key(line.product_id):
                    prods[line.product_id] = {"counted": False, "sold": False, "updated": False, "received": False}
                prods[line.product_id]["sold"] = True
                
        
    return prods


if __name__ == "__main__":
    log.debug("HOST %s, USER: %s" % (STORE_HOST, STORE_USERID))
    api = ApiClient(STORE_HOST, STORE_TOKEN, STORE_USERID)
    
    print api.Products.get_count()
    count = 0
    for product in api.Products.enumerate(start=1000):
        quantity = product.inquire("quantity")
        print count, "-", product.stock_no, product.name, quantity
        count += 1
        
    
    """    
    prods = get_product_qty_adjustment(api, datetime.utcnow()-timedelta(days=10))
    pprint (prods)
    """
    
    """
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
     
        
        pf = api.Products.filters()
        if branch.name != "Head Office":
            pf.branch_id.set(branch.id)
            
        print "Products"
        for p in api.Products.enumerate(start=5, limit=20, query=pf):
            qty = p.inquire("quantity",pf)
            print "\t", p.id, p.name, qty
        
        print "Documents"
        df = api.Documents.filters()
        df["from"].set(datetime.now() - timedelta(days=15))
        if branch.name != "Head Office":
            df.branch_id.set(branch.id)
    
        print api.Documents.get_count(query=df)
        for product in api.Documents.enumerate(limit=10, query=df):
            print product.id
        
            
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
        
    
    d = datetime.utcnow() - timedelta(days=20)
    print "Invoices Since", d
    f = api.Invoices.filters()
    f["from"].set(d)
    
    for invoice in api.Invoices.enumerate(query=f):
        print invoice.id, invoice.invoice_no, invoice.amount
        for line in invoice.invoice_lines:
            print "Line Items", line.product_id, line.price, line.quantity
        pass
    
        
    
    for product in api.Documents.enumerate():
        print product.id
    print datetime.utcnow()
    """