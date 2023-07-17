import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Customers(BaseModel):
    customer_id: int
    customer_name: str

@router.post('/insertCustomer')
def insert_customer(customer: Customers):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO customers (customer_id,customer_name) VALUES (%s,%s)'''
        values = (customer.customer_id, 
                  customer.customer_name)
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Customer has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}