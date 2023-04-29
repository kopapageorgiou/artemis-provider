import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Client(BaseModel):
    client_id: str
    client_name: str

@router.post('/insertClient')
def insert_client(client: Client):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO clients (client_id, client_name) VALUES (%s, %s)'''
        session.execute(query=query, parameters=(client.client_id, client.client_name))
        session.shutdown()
        return {"info": "Client has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}