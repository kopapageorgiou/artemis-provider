import paho.mqtt.client as paho
import json, random, time
from datetime import datetime
from pydantic import BaseModel
broker="10.31.20.57"
port=1883

REPETITIONS = 5
CLIENTS = 2
SAMPLING_RATE = 0.1

regs = {}
rand = random.Random()
types = ["data", "event"]
clients = json.load(open("clients.json"))
gateways = json.load(open("gateways.json"))
vehicles = json.load(open("vehicles.json"))
names = json.load(open("names.json"))
serial = json.load(open("serial.json"))

def on_publish(client, userdata, result):
    print("data published")
    pass

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)

client = paho.Client("control")
client.on_publish = on_publish
client.on_connect = on_connect

client.connect(broker, port)

class Data(BaseModel):
    reg_id: str
    gate_id: int
    latitude: float
    longitude: float
    timestamp: str
    temp: int
    name_temp: str
    overtemp: int
    signal: str
    serial: int
    signature: None
    engine: int

class Event(BaseModel):
    reg_id: str
    gate_id: int
    timestamp: str
    poi_id: str
    order_id: str

def generate_random_data():
    cl = rand.choices(list(clients.keys()))[0]
    serial[cl] += 1
    with open("serial.json", "w") as fp:
        json.dump(serial, fp)
    fp.close()
    return Data(
        reg_id= cl,
        gate_id= gateways[cl],
        latitude= rand.uniform(-90.0, 90.0),
        longitude= rand.uniform(-180.0, 180.0),
        timestamp= datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        temp= rand.randint(-10, 15),
        name_temp= names[cl],
        overtemp= rand.choices([0,1], [99, 1], k=1)[0],
        signal= rand.choices(["H","L"], [80, 20], k=1)[0],
        serial= serial[cl],
        signature= None,
        engine= rand.choices([0,1], [80, 20], k=1)[0]
    )

def generate_random_event():
    cl = rand.choices(list(clients.keys()))[0]
    
    return Event(
        reg_id= cl,
        gate_id= gateways[cl],
        timestamp= datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        poi_id= str(rand.randint(0, 15)),
        order_id= str(rand.randint(30000, 40000))
    )

def generate_random_type():
    chosen_type = rand.choices(types, weights=(70, 30), k=1)[0]
    if chosen_type == "data":
        return chosen_type, generate_random_data()
    else:
        return chosen_type, generate_random_event()

for i in range(REPETITIONS):

    client.loop_start()
    chosen_type, obj = generate_random_type()
    attr = {
        chosen_type: [
            obj.json()
        ]
    }
    ret = client.publish(f"{obj.reg_id}/{obj.gate_id}/{chosen_type}", json.dumps(attr))
    time.sleep(SAMPLING_RATE)
    client.loop_stop()