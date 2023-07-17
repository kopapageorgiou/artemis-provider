import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Shipments(BaseModel):
    shipment_id: str
    shipment_date: int
    vehicle_id: str

@router.post('/insertShipment')
def insert_shipment(shipment: Shipments):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO shipments (shipment_id, shipment_date,vehicle_id) VALUES (%s, %s, %s)'''
        values = (shipment.shipment_id,
                  shipment.shipment_date,
                  shipment.vehicle_id
                  )
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Shipment has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}