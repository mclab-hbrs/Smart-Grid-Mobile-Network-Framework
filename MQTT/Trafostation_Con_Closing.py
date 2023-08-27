import csv
import time
import os
import json
import paho.mqtt.publish as publish

class gvar():
    dictUpdateVal = {}
    dataset = []
    dataset_index = 0

def update_ied_attr():
    '''loading new values into dict'''
    ######################
    # set values
    gvar.dictUpdateVal.clear()
    gvar.dictUpdateVal.update(gvar.dataset[gvar.dataset_index])
    gvar.dictUpdateVal["timestamp"] = time.strftime("%d.%m.%Y, %H:%M:%S")

    if gvar.dataset_index + 1 >= len(gvar.dataset):
        gvar.dataset_index = 0
    else:
        gvar.dataset_index += 1

def run():
    '''main function'''
    # read dataset
    csv_reader = csv.DictReader(open('sample_data.csv'))
    for row in csv_reader:
        gvar.dataset.append(next(csv_reader))
    
    while True:
        time.sleep(60)
        update_ied_attr()
        msg = json.dumps(gvar.dictUpdateVal)
        print("Publishing to topic: "+os.environ.get('CLIENT_NAME')+"/Values")

        # https://pypi.org/project/paho-mqtt/#single
        publish.single(os.environ.get('CLIENT_NAME')+"/Values", msg, hostname=os.environ.get('SERVERIP'), port=int(os.environ.get('TCPPORT')), client_id=os.environ.get('CLIENT_NAME'))

if __name__ == '__main__':
    print(os.environ.get('CLIENT_NAME'))
    run()