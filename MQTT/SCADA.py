#!/usr/bin/python
import os
import sys
import threading
import json
import time

# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python

# lib for MQTT Client
from paho.mqtt import client as mqtt_client

# lib for RESTfull API
from flask import Flask, request, redirect, render_template


class gvar():
    # Content Array
    values = {}

    values["mallsensor1"] = {}
    values["mallsensor2"] = {}
    values["mallsensor3"] = {}
    values["mallsensor4"] = {}
    values["mallsensor5"] = {}

    # client api
    client = None


# Flask REST API
app = Flask(__name__)


@app.route('/')
def index():
    '''main index page'''
    return render_template('index.html', content=gvar.values)

# define API Call


@app.get('/start_test')
def start_test():
    '''define API Call'''
    thread = threading.Thread(target=test_client)
    thread.start()
    return redirect("/", code=302)


def connect_mqtt() -> mqtt_client:
    '''connect to mqtt broker'''

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(os.environ.get('CLIENT_NAME'))

    # client.username_pw_set("test", "1234")
    client.on_connect = on_connect
    client.connect(os.environ.get('SERVERIP'), int(
        os.environ.get('TCPPORT')), keepalive=60)
    return client


def subscribe(client: mqtt_client):
    '''subscribe to a mqtt topic'''
    #topic = os.environ.get('TRAFO_NAME')+"1/Values"
    topic = [(os.environ.get('TRAFO_NAME')+"1/Values", 0), (os.environ.get('TRAFO_NAME')+"2/Values", 0),
             (os.environ.get('TRAFO_NAME')+"3/Values", 0), (os.environ.get('TRAFO_NAME')+"4/Values", 0),
             (os.environ.get('TRAFO_NAME')+"5/Values", 0)]

    def on_message(client, userdata, msg):
        print(f"Received Msg from `{msg.topic}` topic")
        tmp = msg.payload.decode()
        key = msg.topic.split("/")[0]
        print(key)
        gvar.values[key].update(json.loads(tmp))

    client.subscribe(topic)
    client.on_message = on_message


def test_client():
    ''' Main function for mqtt client'''

    gvar.client = connect_mqtt()
    subscribe(gvar.client)
    gvar.client.loop_start()
    time.sleep(3650)  # 3600s = 1h | 50s tollerance 
    gvar.client.loop_stop()
    os._exit(1)  # end program not only thread


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
