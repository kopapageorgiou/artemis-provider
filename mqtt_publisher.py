import paho.mqtt.client as paho

broker="10.31.20.57"
port=1883

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
client.loop_start()
ret = client.publish("testTopic/testData", "testPayload")
client.loop_stop()