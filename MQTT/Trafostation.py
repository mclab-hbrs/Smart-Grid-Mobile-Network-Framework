import csv
import random
import time
import os
from paho.mqtt import client as mqtt_client
import json

# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python

class gvar():
    dictUpdateVal = {}
    dataset = []
    dataset_index = 0

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(os.environ.get('CLIENT_NAME'))

    #client.username_pw_set("test", "1234")
    client.on_connect = on_connect
    client.connect(os.environ.get('SERVERIP'), int(os.environ.get('TCPPORT')), keepalive=60)
    return client

def update_IED_attr():
    ######################
    # set values
    gvar.dictUpdateVal.clear()
    gvar.dictUpdateVal.update(gvar.dataset[gvar.dataset_index])
    gvar.dictUpdateVal["timestamp"] = time.strftime("%d.%m.%Y, %H:%M:%S")

    if gvar.dataset_index + 1 >= len(gvar.dataset):
        gvar.dataset_index = 0
    else:
        gvar.dataset_index += 1

def publish(client):
    msg_count = 0
    while True:
        time.sleep(60)
        #time.sleep(900) # 15min
        update_IED_attr()
        msg = json.dumps(gvar.dictUpdateVal)
        #msg = f"messages: {msg_count}"
        result = client.publish(os.environ.get('CLIENT_NAME')+"/Values", msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send Msg to topic `{os.environ.get('CLIENT_NAME')}`")
        else:
            print(f"Failed to send message to topic {os.environ.get('CLIENT_NAME')}")
        msg_count += 1

def run():
    # read dataset
    csv_reader = csv.DictReader(open('sample_data.csv'))
    for row in csv_reader:
        gvar.dataset.append(next(csv_reader)) 
    
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()