import paho.mqtt.client as mqtt
import time
import os

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

broker_address= os.environ['MQTT_BROKER']
port = 1883

print("creating new instance")
client = mqtt.Client("P1", clean_session=False)
client.on_message=on_message
print("connecting to broker")
client.connect(broker_address, port)
print("Subscribing to topic","testTopic/testData")
client.subscribe("testTopic/testData")
client.loop_forever()