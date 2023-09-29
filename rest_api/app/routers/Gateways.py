import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Gateway(BaseModel):
    gateway_id: int
    gateway_description: str
    vehicle_id: str
    client_id: int

@router.post('/insertGateway')
def insert_client(gateway: Gateway):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO gateways
        (gateway_id, gateway_description, vehicle_id, client_id)
        VALUES (%s, %s, %s, %s)'''
        values = (gateway.gateway_id,
                  gateway.gateway_description,
                  gateway.vehicle_id,
                  gateway.client_id, )
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Gateway has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}