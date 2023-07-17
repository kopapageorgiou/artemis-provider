import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Orders(BaseModel):
    order_id: str
    customer_id: str
    stop_id: str
    shipment_id: str

@router.post('/insertOrders')
def insert_orders(order: Orders):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO orders (order_id, customer_id,stop_id,shipment_id) VALUES (%s, %s, %s)'''
        values = (order.order_id,
                  order.customer_id,
                  order.stop_id,
                  order.shipment_id
                  )
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Order has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}