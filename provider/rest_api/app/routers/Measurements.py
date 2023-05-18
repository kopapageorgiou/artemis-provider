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
    order_id: str #Must be known from the caller
    measurement_id: int
    measurement_value: int
    measurement_timestamp: str
    measurement_location: str
    current_stop_id: str
    sensor_id: str

flags = {}
keys = {}

@router.post('/insertMeasurement')
def insert_client(measurement: Measurement):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO measurements
        (measurement_id, current_stop_id, measurement_location, measurement_time, measurement_value, sensor_id)
        VALUES (%s, %s, %s, %s, %s, %s)'''

        values = (measurement.measurement_id,
                    measurement.current_stop_id,
                    measurement.measurement_location,
                    measurement.measurement_timestamp,
                    measurement.measurement_value,
                    measurement.sensor_id, )
        session.execute(query=query, parameters=values)
        query = '''SELECT * FROM sensors WHERE sensor_id = %s'''
        gateway_id = session.execute(query, (measurement.sensor_id,)).one().gateway_id
        query = '''SELECT vehicle_id FROM gateways WHERE gateway_id = %s'''
        vehicle_id = session.execute(query, (gateway_id,)).one().vehicle_id
        session.shutdown()
        checkStop(vehicle_id, int(measurement.current_stop_id))
        enc_measurement_value = encrypt(keys[vehicle_id], str(measurement.measurement_value))
        enc_measurement_time = encrypt(keys[vehicle_id], measurement.measurement_timestamp)
        enc_measurement_location = encrypt(keys[vehicle_id], measurement.measurement_location)
        orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
        db = orbitdb.load(dbname='shared.measurements')
        res = db.insertMeasurements({
            "order_id": measurement.order_id,
            "measurement_id": measurement.measurement_id,
            "sensor_id": measurement.sensor_id,
            "enc_measurement_value": enc_measurement_value,
            "enc_measurement_time": enc_measurement_time,
            "enc_measurement_location": enc_measurement_location,
            "abe_enc_key": keys[vehicle_id]
            
        })
        return {"info": "Measurement has been imported successfully", "code": 1, "debug": res}
    except Exception as e:
        logging.debug(e)
        return {"info": e, "code": 0}

def checkStop(vehicle_id, stop_id):
    logging.debug("Checking for stop")
    if vehicle_id in flags:
        logging.debug("vehicle exist with key")
        if flags[vehicle_id] == 1 and stop_id == 0:
            logging.debug("switching keys")
            flags[vehicle_id] = 0
            keys[vehicle_id] = generateSymmetricKey()

    else:
        logging.debug("vehicle register 1st time")
        flags[vehicle_id] = 0
        keys[vehicle_id] = generateSymmetricKey()
    
def generateSymmetricKey():
    logging.debug("Generating key")
    return base64.b64encode(get_random_bytes(32)).decode('utf-8')

def encrypt(key, value):
    key = key.encode('utf-8')
    key = base64.b64decode(key)
    cipher = AES.new(key, AES.MODE_CBC)
    logging.debug("Encrypting data")
    return base64.b64encode(cipher.encrypt(pad(bytes(value, 'utf-8'), AES.block_size))).decode('utf-8')
                
