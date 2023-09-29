import paho.mqtt.client as mqtt
import time, json, os, requests, random

#broker_address= os.environ['MQTT_BROKER'] #This is for local test of mqtt
broker_address = "artemis-mqtt.itrack.gr"
REST_API_ADDRESS = "http://"+os.environ['REST_API']+":8000"
port = 1883

def handle_data(payload: dict):

    attrs = {
        "order_id": f"{random.Random().randint(1000,2000)}",
        "gateway_id": payload['gate_id'],
        "measurement_id": int(f"{payload['gate_id']}{payload['serial']}"),
        "measurement_value": payload['temp'],
        "measurement_timestamp": payload['timestamp'],
        "measurement_location": f"{random.Random().uniform(-90.0, 90.0)}, {random.Random().uniform(-180.0, 180.0)}",
        "sensor_id": str(f"{payload['gate_id']}{payload['name_temp']}")
    }
    response = requests.post(REST_API_ADDRESS+"/insertMeasurement", json=attrs)
    print(response.json())

def handle_event(payload: dict): 
    if type(payload['poi_id']) == int:
        payload['poi_id'] = str(payload['poi_id'])
    attr = {
        "gateway_id": payload['gate_id'],
        "poi_id": payload['poi_id']
    }
    print("Response: ", attr)
    response = requests.post(REST_API_ADDRESS+"/generateKey", json= attr)
    print(response.json())
 
def on_message(client, userdata, message):
    topic = message.topic.split("/")
    client_id = topic[0]
    gateway_id = topic[1]
    payload_type = topic[2]
    print(str(message.payload.decode("utf-8")))
    if payload_type == "data":
        p1 = json.loads(str(message.payload.decode("utf-8")))['data'][0]
        handle_data(p1)
    else:
        try:
            p1 = json.loads(str(message.payload.decode("utf-8")))['event'][0]
        except:
            p1 = json.loads(str(message.payload.decode("utf-8")))['event']
        handle_event(p1)
    # print("client id =", client_id)
    # print("gateway_id =", gateway_id)
    # print("type =", payload_type)
    # print("here")
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("19800/+/data", qos=2)
    client.subscribe("19800/+/events", qos=2)
    client.subscribe("19800/+/commit", qos=2)
print("creating new instance")
client = mqtt.Client("", clean_session=True)
client.username_pw_set(username="thessaly",password="En2icbTE")
client.on_message=on_message
client.on_connect = on_connect
print("connecting to broker")
client.connect(broker_address, port)
print("Subscribing to topic","")
#client.subscribe("19800/+/#")
client.loop_forever()