import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Measurement(BaseModel):
    measurement_id: int
    measurement_value: int
    measurement_timestamp: str
    measurement_location: str
    current_stop_id: str
    sensor_id: str


@router.post('/insertMeasurement')
def insert_client(measurement: Measurement):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO gateways
        (measurement_id, measurement_value, measurement_timestamp, measurement_location, current_stop_id, sensor_id)
        VALUES (%s, %s, %s, %s)'''
        values = (measurement.gateway_id,
                  measurement.gateway_description,
                  measurement.vehicle_id,
                  measurement.client_id)
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Measurement has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}