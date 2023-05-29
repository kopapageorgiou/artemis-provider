import paho.mqtt.client as mqtt
import time, json, os, requests, random

broker_address= os.environ['MQTT_BROKER']
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
        "current_stop_id": "0",
        "sensor_id": str(f"{payload['gate_id']}{payload['name_temp']}")
    }
    response = requests.post(REST_API_ADDRESS+"/insertMeasurement", json=attrs)
    print(response.json())

def handle_event(payload: dict):
    attr = {
        "gateway_id": payload['gate_id']
    }
    response = requests.post(REST_API_ADDRESS+"/generateKey", json= attr)
    print(response.json())

def on_message(client, userdata, message):
    topic = message.topic.split("/")
    client_id = topic[0]
    gateway_id = topic[1]
    payload_type = topic[2]
    if payload_type == "data":
        p1 = json.loads(str(message.payload.decode("utf-8")))['data'][0]
        handle_data(json.loads(p1))
    else:
        p1 = json.loads(str(message.payload.decode("utf-8")))['event'][0]
        handle_event(json.loads(p1))
    # print("client id =", client_id)
    # print("gateway_id =", gateway_id)
    # print("type =", payload_type)
    # print("here")

print("creating new instance")
client = mqtt.Client("P1", clean_session=False)
client.on_message=on_message
print("connecting to broker")
client.connect(broker_address, port)
print("Subscribing to topic","")
client.subscribe("#")
client.loop_forever()