import os, sys
from fastapi import APIRouter, Request
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
    gateway_id: int
    measurement_id: int
    measurement_value: int
    measurement_timestamp: str
    measurement_location: str
    current_stop_id: str
    sensor_id: str

flags = {}

@router.post('/insertMeasurement')
def insert_client(measurement: Measurement, request: Request):
    try:
        logging.debug("1a")
        session = cluster.connect('mkeyspace')
        logging.debug("1b")
        query = '''INSERT INTO measurements
        (measurement_id, current_stop_id, measurement_location, measurement_time, measurement_value, sensor_id)
        VALUES (%s, %s, %s, %s, %s, %s)'''

        values = (measurement.measurement_id,
                    measurement.current_stop_id,
                    measurement.measurement_location,
                    measurement.measurement_timestamp,
                    measurement.measurement_value,
                    measurement.sensor_id, )
        logging.debug("1c")
        session.execute(query=query, parameters=values)
        logging.debug("1d")
        query = '''SELECT * FROM sensors WHERE sensor_id = %s'''
        logging.debug("1e")
        #gateway_id = session.execute(query, (measurement.sensor_id,)).one().gateway_id
        gateway_id = measurement.gateway_id
        logging.debug("1f")
        session.shutdown()
        logging.debug("1g")
        #checkStop(vehicle_id, int(measurement.current_stop_id))
        logging.debug(request.app.state.gate_keys)
        key = request.app.state.gate_keys[gateway_id]
        logging.debug("1")
        #logging.debug(key)
        enc_measurement_value = encrypt(key, str(measurement.measurement_value))
        logging.debug("2")
        enc_measurement_time = encrypt(key, measurement.measurement_timestamp)
        logging.debug("3")
        enc_measurement_location = encrypt(key, measurement.measurement_location)
        logging.debug("4")
        orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
        logging.debug("5")
        db = orbitdb.load(dbname='shared.measurements')
        logging.debug("6")
        res = db.insertMeasurements({
            "order_id": measurement.order_id,
            "measurement_id": measurement.measurement_id,
            "sensor_id": measurement.sensor_id,
            "enc_measurement_value": enc_measurement_value,
            "enc_measurement_time": enc_measurement_time,
            "enc_measurement_location": enc_measurement_location,
            "abe_enc_key": key
            
        })
        logging.debug("7")
        return {"info": "Measurement has been imported successfully", "code": 1, "debug": res}
    except Exception as e:
        logging.debug(e)
        return {"info": e, "code": 0}

# ! DEPRICATED! Probably will get removed
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
# ! DEPRICATED! Probably will get removed    
def generateSymmetricKey():
    logging.debug("Generating key")
    return base64.b64encode(get_random_bytes(32)).decode('utf-8')

def encrypt(key, value):
    key = key.encode('utf-8')
    key = base64.b64decode(key)
    cipher = AES.new(key, AES.MODE_CBC)
    logging.debug("Encrypting data")
    return base64.b64encode(cipher.encrypt(pad(bytes(value, 'utf-8'), AES.block_size))).decode('utf-8')
                
