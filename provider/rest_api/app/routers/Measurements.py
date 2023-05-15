import os, sys
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import requests
import logging
parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_folder_path)
from Orbitdbapi import OrbitdbAPI


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
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
        logging.debug("0")
        query = '''INSERT INTO measurements
        (measurement_id, current_stop_id, measurement_location, measurement_time, measurement_value, sensor_id)
        VALUES (%s, %s, %s, %s, %s, %s)'''
        logging.debug("00")
        values = (measurement.measurement_id,
                    measurement.current_stop_id,
                    measurement.measurement_location,
                    measurement.measurement_timestamp,
                    measurement.measurement_value,
                    measurement.sensor_id)
        logging.debug("01")
        logging.debug("0a")
        session.execute(query=query, parameters=values)
        logging.debug("0b")
        session.shutdown()
        logging.debug("1")
        orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
        logging.debug("2")
        res = orbitdb.insertMeasurements({
            "order_id": 2,
            "measurement_id": measurement.measurement_id,
            "sensor_id": measurement.sensor_id,
            "enc_measurement_value": measurement.measurement_value,
            "enc_measurement_time": measurement.measurement_timestamp,
            "enc_measurement_location": measurement.measurement_location,
            "abe_enc_key": 'test',
            
        })
        logging.debug("3")
        return {"info": "Measurement has been imported successfully", "code": 1, "debug": res}
    except Exception as e:
        logging.debug(e)
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
                
