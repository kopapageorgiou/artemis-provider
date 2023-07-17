import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Vehicles(BaseModel):
    vehicle_id: str

@router.post('/insertVehicles')
def insert_vehicles(vehicle: Vehicles):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO vehicles (vehicle_id) VALUES (%s)'''
        values = (vehicle.vehicle_id)
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Vehicle has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}