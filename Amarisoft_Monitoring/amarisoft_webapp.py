import asyncio
import os
import time
from datetime import datetime
import websocket
import json
import csv


async def run():
    print(ws.recv())  # connection msg

    header = ["sat_tx", "sat_rx", "rms_sample_tx", "max_sample_tx", "rms_sample_rx", "max_sample_rx", "dl_tx", "ul_tx", "dl_retx", "ul_retx", "dl_bitrate", "ul_bitrate", 
              "rxtx_delay_avg", "rxtx_delay_max", "s1_setup_requests", "s1_setup_response", "s1_initial_ue_message", "s1_ue_context_release_complete", "prach", 
              "rrc_ue_capability_information", "rrc_ul_information_transfer", "rrc_dl_information_transfer", "rrc_connection_request", "rrc_connection_setup", 
              "rrc_connection_release", "ul_use_avg", "dl_use_avg", "ul_use_max", "dl_use_max", "ue_inactive_count_max", "ue_count_max", "duration", "Timestamp", "ue_list"]
    
    file_name = '/work/log/monitoring_data.csv'
    if os.path.isfile(file_name) == True:
        file_name = '/work/log/monitoring_data_new.csv'

    with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:    # mode 'a' append
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(header)

        while True:
            # os.system('clear')
            tmp_values = {}

            ws.send('{"message": "stats", "samples": true}')
            msg_stat = json.loads(str(ws.recv()))

            if 'samples' in msg_stat.keys():
                tmp_values["sat_tx"] = str(msg_stat["samples"]["tx"][0]["sat"])
                tmp_values["sat_rx"] = str(msg_stat["samples"]["rx"][0]["sat"])

                tmp_values["rms_sample_tx"] = str(msg_stat["samples"]["tx"][0]["rms"])
                tmp_values["max_sample_tx"] = str(msg_stat["samples"]["tx"][0]["max"])
                
                tmp_values["rms_sample_rx"] = str(msg_stat["samples"]["rx"][0]["rms"])
                tmp_values["max_sample_rx"] = str(msg_stat["samples"]["rx"][0]["max"])
            else: 
                print("Warning no Sample")
                tmp_values["sat_tx"] = 0
                tmp_values["sat_rx"] = 0
                tmp_values["rms_sample_tx"] = 0
                tmp_values["max_sample_tx"] = 0
                tmp_values["rms_sample_rx"] = 0
                tmp_values["max_sample_rx"] = 0

            tmp_values["dl_tx"] = str(msg_stat["cells"]["1"]["dl_tx"])
            tmp_values["ul_tx"] = str(msg_stat["cells"]["1"]["ul_tx"])
            tmp_values["dl_retx"] = str(msg_stat["cells"]["1"]["dl_retx"])
            tmp_values["ul_retx"] = str(msg_stat["cells"]["1"]["ul_retx"])
            tmp_values["dl_bitrate"] = str(msg_stat["cells"]["1"]["dl_bitrate"])+"Bit/s"
            tmp_values["ul_bitrate"] = str(msg_stat["cells"]["1"]["ul_bitrate"])+"Bit/s"
            tmp_values["rxtx_delay_avg"] = str( msg_stat["rf_ports"]["0"]["rxtx_delay"]["avg"])+"ms"
            tmp_values["rxtx_delay_max"] = str(msg_stat["rf_ports"]["0"]["rxtx_delay"]["max"])+"ms"
            
            # S1 messages
            if 's1_setup_request' in msg_stat["counters"]["messages"].keys():
                tmp_values["s1_setup_requests"] = str(msg_stat["counters"]["messages"]["s1_setup_request"])
            else:
                tmp_values["s1_setup_requests"] = 0

            if 's1_setup_response' in msg_stat["counters"]["messages"].keys():
                tmp_values["s1_setup_response"] = str(msg_stat["counters"]["messages"]["s1_setup_response"])
            else:
                tmp_values["s1_setup_response"] = 0

            if 's1_initial_ue_message' in msg_stat["counters"]["messages"].keys():
                tmp_values["s1_initial_ue_message"] = str(msg_stat["counters"]["messages"]["s1_initial_ue_message"])
            else:
                tmp_values["s1_initial_ue_message"] = 0

            if 's1_ue_context_release_complete' in msg_stat["counters"]["messages"].keys():
                tmp_values["s1_ue_context_release_complete"] = str(
                    msg_stat["counters"]["messages"]["s1_ue_context_release_complete"])
            else:
                tmp_values["s1_ue_context_release_complete"] = 0
            
            # RRC messages
            if 'prach' in msg_stat["cells"]["1"]["counters"]["messages"].keys():
                tmp_values["prach"] = str(
                    msg_stat["cells"]["1"]["counters"]["messages"]["prach"])
            else:
                tmp_values["prach"] = 0
            
            if 'rrc_ue_capability_information' in msg_stat["cells"]["1"]["counters"]["messages"].keys():
                tmp_values["rrc_ue_capability_information"] = str(
                    msg_stat["cells"]["1"]["counters"]["messages"]["rrc_ue_capability_information"])
            else:
                tmp_values["rrc_ue_capability_information"] = 0
            
            if 'rrc_ul_information_transfer' in msg_stat["cells"]["1"]["counters"]["messages"].keys():
                tmp_values["rrc_ul_information_transfer"] = str(
                    msg_stat["cells"]["1"]["counters"]["messages"]["rrc_ul_information_transfer"])
            else:
                tmp_values["rrc_ul_information_transfer"] = 0

            if 'rrc_dl_information_transfer' in msg_stat["cells"]["1"]["counters"]["messages"].keys():
                tmp_values["rrc_dl_information_transfer"] = str(
                     msg_stat["cells"]["1"]["counters"]["messages"]["rrc_dl_information_transfer"])
            else:
                tmp_values["rrc_dl_information_transfer"] = 0

            if 'rrc_connection_request' in msg_stat["cells"]["1"]["counters"]["messages"].keys():
                tmp_values["rrc_connection_request"] = str(
                     msg_stat["cells"]["1"]["counters"]["messages"]["rrc_connection_request"])
            else:
                tmp_values["rrc_connection_request"] = 0

            if 'rrc_connection_setup' in msg_stat["cells"]["1"]["counters"]["messages"].keys():
                tmp_values["rrc_connection_setup"] = str(
                     msg_stat["cells"]["1"]["counters"]["messages"]["rrc_connection_setup"])
            else:
                tmp_values["rrc_connection_setup"] = 0
            
            if 'rrc_connection_release' in msg_stat["cells"]["1"]["counters"]["messages"].keys():
                tmp_values["rrc_connection_release"] = str(
                     msg_stat["cells"]["1"]["counters"]["messages"]["rrc_connection_release"])
            else:
                tmp_values["rrc_connection_release"] = 0

            tmp_values["ul_use_avg"] = str(msg_stat["cells"]["1"]["ul_use_avg"])
            tmp_values["dl_use_avg"] = str(msg_stat["cells"]["1"]["dl_use_avg"])
            tmp_values["ul_use_max"] = str(msg_stat["cells"]["1"]["ul_use_max"])
            tmp_values["dl_use_max"] = str(msg_stat["cells"]["1"]["dl_use_max"])
            tmp_values["ue_inactive_count_max"] = str(msg_stat["cells"]["1"]["ue_inactive_count_max"])
            tmp_values["ue_count_max"] = str(msg_stat["cells"]["1"]["ue_count_max"])
            tmp_values["duration"] = str(msg_stat["duration"])
            tmp_values["Timestamp"] = str(datetime.fromtimestamp(msg_stat["utc"]).__str__())

            ws.send('{"message": "ue_get", "stats": true}')
            msg_ues = json.loads(str(ws.recv()))
            print(msg_ues)

            tmp_values["ue_list"] = str(msg_ues["ue_list"])

            csv_writer.writerow(list(tmp_values.values()))
            time.sleep(1)  # determines the polling interval

if __name__ == "__main__":
    ws = websocket.WebSocket()

    while not ws.connected:
        try:
            ws.connect("ws://"+str(os.environ.get('SERVERIP')) +
                       ":"+str(os.environ.get('PORT')))
            print("connected")
        except:
            print("No connection. Trying again in 5s")
            time.sleep(5)

    asyncio.get_event_loop().run_until_complete(run())
