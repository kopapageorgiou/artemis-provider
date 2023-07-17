import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Sensor(BaseModel):
    sensor_id: str
    sensor_type: str
    gateway_id: int

@router.post('/insertSensor')
def insert_client(sensor: Sensor):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO sensors
        (sensor_id, sensor_type, gateway_id)
        VALUES (%s, %s, %s)'''
        values = (sensor.sensor_id,
                  sensor.sensor_type,
                  sensor.gateway_id, )
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Sensor has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}