import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Batches(BaseModel):
    batch_id: int

@router.post('/insertBatch')
def insert_batch(batch: Batches):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO batches (batch_id) VALUES (%s)'''
        values = (batch.batch_id)
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Batch has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}