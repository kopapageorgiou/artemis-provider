import paho.mqtt.client as mqtt
import time, json, os, requests, random, json, pickle
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from threading import Thread

addid = json.load(open("current_prefix.json"))["prefix"]
#broker_address= os.environ['MQTT_BROKER'] #This is for local test of mqtt
broker_address = "artemis-mqtt.itrack.gr"
REST_API_ADDRESS = "http://"+os.environ['REST_API']+":8000"
port = 1883
orders = {}
legs_temp = {}
legs = {}
data_to_sign = []
start_calling = False

def setup_publisher():
    """Setup the MQTT publisher client."""
    publisher = mqtt.Client("", clean_session=True)
    publisher.username_pw_set(username="gateway_14300", password="qGndLpmT")
    publisher.connect(broker_address, port)
    return publisher

print("creating new instance")
client = mqtt.Client("", clean_session=True)

def handle_commit(payload: dict):
    attrs = {
        "hash_string": payload['hash'],
        "signature": payload['signature'],
        "gateway_id": payload['gate_id'],
        "begin_t": payload['begin_t'],
        "end_t": payload['end_t']
    }
    response = requests.post(REST_API_ADDRESS+"/commit", json=attrs)
    print(response.json())

def handle_orders(payload: dict):
    gateway_id = int(payload['orders'][0]['gate_id'])
    orders[gateway_id] = payload['order_id']
    legs[gateway_id] = [str(order['poi_id']) for order in payload['orders']]
    if '1' in orders[gateway_id]:
        legs[gateway_id].remove('1')
    legs_temp[gateway_id] = legs[gateway_id].copy()
    print("Legs:", legs)


def handle_data(payload: dict, gateway_id):
    global start_calling, addid, data_to_sign
    if start_calling:
        addid +=1
        if len(data_to_sign) == 10:
            t = Thread(target=publish_commit, args=(data_to_sign.copy(), f"19800/{gateway_id}/commit",))
            t.start()
            data_to_sign.clear()
        try:
            attrs = {
            "order_id": orders[payload['gate_id']],
            "gateway_id": payload['gate_id'],
            "measurement_id": int(f"{payload['gate_id']}{addid}"),
            "measurement_value": payload['temp'],
            "measurement_timestamp": payload['timestamp'],
            "measurement_location": f"{payload['latitude']}, {payload['longitude']}",
            "sensor_id": str(f"{payload['gate_id']}{payload['name_temp']}")
            }
            response = requests.post(REST_API_ADDRESS+"/insertMeasurement", json=attrs)
            print(response.json())
            json.dump({"prefix": addid}, open("current_prefix.json", "w"))
            data_to_sign.append(payload)
        except Exception as e:
            pass
    else:
        print("Not calling yet for Data")
    

def handle_event(payload: dict): 
    global start_calling
    if payload['poi_id'] == 1:
        start_calling = True
        print("Adding order, legs to API:", legs[payload['gate_id']], orders[payload['gate_id']]) #Will be replaced
        attr = {
            "device_id": payload['gate_id'],
            "leg": legs[payload['gate_id']],
            "order_id": orders[payload['gate_id']]
        }
        response = requests.post(REST_API_ADDRESS+"/insertStations", json= attr)
    if not legs_temp[payload['gate_id']]:
        print("No more legs")
        attr = {
            "device_id": payload['gate_id'],
            "leg": legs[payload['gate_id']],
            "order_id": orders[payload['gate_id']]
        }
        response = requests.post(REST_API_ADDRESS+"/insertStations", json= attr)
    if start_calling and payload['poi_id'] != 1:
        try:
            payload['poi_id'] = str(payload['poi_id'])
            # if type(payload['order_id']) == int:
            #     payload['order_id'] = str(payload['order_id'])
            attr = {
                "gateway_id": payload['gate_id'],
                "poi_id": payload['poi_id']
                #"order_id": payload['order_id'],
            }
            #print("Response: ", attr)
            response = requests.post(REST_API_ADDRESS+"/generateKey", json= attr)
            print(response.json())
            legs_temp[payload['gate_id']].remove(payload['poi_id'])
        except Exception as e:
            pass 
 
def on_message(client, userdata, message):
    topic = message.topic.split("/")
    client_id = topic[0]
    gateway_id = topic[1]
    payload_type = topic[2]
    print(str(message.payload.decode("utf-8")))
    if payload_type == "data":
        p1 = json.loads(str(message.payload.decode("utf-8")))['data'][0]
        handle_data(p1, gateway_id)
    elif payload_type == "events":
        try:
            p1 = json.loads(str(message.payload.decode("utf-8")))['event'][0]
        except:
            p1 = json.loads(str(message.payload.decode("utf-8")))['event']
        handle_event(p1)
        print(p1)
    elif payload_type == "commit":
        p1 = json.loads(str(message.payload.decode("utf-8")))
        handle_commit(p1)
    else:
        p1 = json.loads(str(message.payload.decode("utf-8")))
        handle_orders(p1)
    #print(payload_type, p1)
    # print("client id =", client_id)
    # print("gateway_id =", gateway_id)
    # print("type =", payload_type)
    # print("here")
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("19800/+/data", qos=2)
    client.subscribe("19800/+/events", qos=2)
    client.subscribe("19800/+/commit", qos=2)
    client.subscribe("19800/+/orders", qos=2)



def publish_commit(data_to_sign, topic="19800/+/commit"):
    """
    Publishes the given data to the MQTT broker using the provided client.

    Args:
        client: An instance of the MQTT client.
        data: The data to be published.

    Returns:
        None
    """
    publisher = mqtt.Client("", clean_session=True)
    publisher.username_pw_set(username="gateway_14300", password="qGndLpmT")
    publisher.connect(broker_address, port)
    data = create_signature(data_to_sign)
    #msg_dict = {"commit": [data]}
    msg = json.dumps(data)

    result = publisher.publish(topic, msg)

    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def create_signature(data:list):
    """
    Generate a JSON commit with a signature.

    Args:
        data (list): A list containing the data to be committed.

    Returns:
        dict: A dictionary containing the generated JSON payload.

    Raises:
        None
    """
    # SHA256 hash the data and RSA sign them
    with open("privkey.dat", "rb") as f:
        secret_key = pickle.load(f)
    p_key = RSA.importKey(secret_key)
    filtered_data = [{key: value for key, value in d.items() if key in ["timestamp", "temp"]} for d in data]
    data_to_sign = json.dumps(filtered_data, sort_keys=True).encode("utf-8")
    print("Data to sign:", filtered_data)
    hash = SHA256.new(data_to_sign)
    signature = PKCS1_v1_5.new(p_key).sign(hash)

    # find earliest timestamp in data (list of JSON objects)
    earliest_timestamp = min(filtered_data, key=lambda x: x["timestamp"])[
        "timestamp"
    ]

    # find latest timestamp in data (list of JSON objects)
    latest_timestamp = max(filtered_data, key=lambda x: x["timestamp"])[
        "timestamp"
    ]

    # append signature to data and send
    data_to_send = {
        "hash": hash.hexdigest(),
        "signature": signature.hex(),
        "gate_id": "14300",
        "begin_t": earliest_timestamp,
        "end_t": latest_timestamp,
    }

    return data_to_send
client.username_pw_set(username="thessaly",password="En2icbTE")
client.on_message=on_message
client.on_connect = on_connect
print("connecting to broker")
client.connect(broker_address, port)
print("Subscribing to topic","")
# attr = {
#     "device_id": 14300,
#     "poi_id": ["1"],
#     "order_id": "1",
# }
#response = requests.post(REST_API_ADDRESS+"/insertStations", json= attr)
#client.subscribe("19800/+/#")
client.loop_forever()