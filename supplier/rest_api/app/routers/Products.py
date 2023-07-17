import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Products(BaseModel):
    product_id: str
    batch_id: int
    order_id: str

@router.post('/insertProducts')
def insert_products(product: Products):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO products (product_id, batch_id,order_id) VALUES (%s, %s, %s)'''
        values = (product.product_id,
                  product.batch_id,
                  product.order_id
                  )
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Product has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}