import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import requests


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Measurement(BaseModel):
    measurement_id: int
    measurement_value: int
    measurement_timestamp: str
    measurement_location: str
    current_stop_id: str
    sensor_id: str

flags = {}

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

def checkStop(vehicle_id, stop_id):
    if vehicle_id in flags:
        if flags[vehicle_id] == 1 and stop_id == 0:
            flags[vehicle_id] = 0
            key = generateSymmetricKey()

    else:
        flags[vehicle_id] = 0
        key = generateSymmetricKey()

def generateSymmetricKey():
    return get_random_bytes(32)

def encrypt(key, value):
    cipher = AES.new(key, AES.MODE_CBC)
    return base64.b64encode(cipher.encrypt(pad(value, AES.block_size)))
                
