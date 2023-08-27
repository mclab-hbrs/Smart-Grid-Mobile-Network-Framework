'''Programm for connecting to an IEC 61850 MMS Server, e.g. a Substation.'''
import os
import threading
import time

# lib for IEC61850
import iec61850

# lib for RESTfull API
from flask import Flask, request, render_template, redirect


class gvar():
    '''class for global vars'''
    # Content Array
    iec_values = {}

    # val for config
    configRev = {}

    # time the experiment is over
    completionTime = 0

    # dict for dataset vars
    dataset_structure = {}


# lib for IEC61850 traffic

# Flask REST API
app = Flask(__name__)


@app.route('/')
def index():
    '''main index page'''
    return render_template('index.html', content=gvar.iec_values)


@app.get('/start_test')
def start_test():
    '''define API Call'''
    array = str(os.environ.get('SERVERIP')).split(",")
    
    for index, ip in enumerate(array, start=1):
        thread = threading.Thread(target=test_client,args=(ip,index,))
        thread.start()
    return redirect("/", code=302)


def get_vars_one_by_one(con):
    ''' function to call the vars one by one, which is less efficient than datasets '''

    # Guidelines Modelling https://www.dke.de/resource/blob/1622846/54ac5a80df67f199302335e8ece13421/ak952-0-1-modellierungsrichtlinie-v10-new-data.pdf
    # Guidelines FC Vals https://support.mz-automation.de/doc/libiec61850/net/latest/namespace_i_e_c61850_1_1_common.html#a8dfca91707b322017feba10b7f84aa1d

    # Get Values
    gvar.iec_values["Timestamp"] = "Last Update: "+time.strftime("%H:%M:%S")
    gvar.iec_values["MMXU0.TotVAr"] = "MMXU0.TotVAr: "+str(round(iec61850.IedConnection_readFloatValue(
        con, gvar.iec_values["LD_name"]+"/MMXU_MV.TotVAr.mag.f", iec61850.IEC61850_FC_MX)[0], 2))+" W"
    gvar.iec_values["MMXU0.TotW"] = "MMXU0.TotW: "+str(round(iec61850.IedConnection_readFloatValue(
        con, gvar.iec_values["LD_name"]+"/MMXU_MV.TotW.mag.f", iec61850.IEC61850_FC_MX)[0], 2))+" W"
    gvar.iec_values["MMXU0.Hz"] = "MMXU0.Hz: "+str(round(iec61850.IedConnection_readFloatValue(
        con, gvar.iec_values["LD_name"]+"/MMXU_MV.Hz.mag.f", iec61850.IEC61850_FC_MX)[0], 2))+" Hz"

    mmxu_devices = ["MMXU_MV", "MMXU_LV_1", "MMXU_LV_2", "MMXU_LV_3"]
    values = [".A.phsA.cVal.mag.f", ".A.phsB.cVal.mag.f", ".A.phsC.cVal.mag.f",
              ".PhV.phsA.cVal.mag.f", ".PhV.phsB.cVal.mag.f", ".PhV.phsC.cVal.mag.f"]

    for dev in mmxu_devices:
        for var in values:
            if "PhV" in var:
                gvar.iec_values[dev+var[0:9]] = ": " + str(round(iec61850.IedConnection_readFloatValue(
                    con, gvar.iec_values["LD_name"]+"/"+dev+var, iec61850.IEC61850_FC_MX)[0], 2)) + "kV"
            else:
                gvar.iec_values[dev+var[0:7]] = ": " + str(round(iec61850.IedConnection_readFloatValue(
                    con, gvar.iec_values["LD_name"]+"/"+dev+var, iec61850.IEC61850_FC_MX)[0], 2)) + "A"


def check_if_conf_changed(con, nr):
    ''' function for requesting the model from the IEC61850 server '''

    # The read service requested in all cases an object LLN0$DC$NamPlt$configRev
    # Source: "Description of IEC 61850 Communication" p.54
    [lln0_namplt_config_rev, error] = iec61850.IedConnection_readStringValue(
        con, f"mallsensor{str(nr)}_Trafo/LLN0.NamPlt.configRev", iec61850.IEC61850_FC_DC)
    # Hard coded -> should be vars

    # The response contains one item (visible string) with the same value.
    # This means, that configuration does not change during monitoring.
    # Source: "Description of IEC 61850 Communication" p.54

    if nr not in gvar.configRev.keys():
        gvar.configRev[nr] = 0

    if lln0_namplt_config_rev != gvar.configRev[nr]:
        # get device
        [device_list, error] = iec61850.IedConnection_getLogicalDeviceList(con)
        device = iec61850.LinkedList_getNext(device_list)
        # set domain name
        gvar.iec_values["LD_name"] = iec61850.toCharP(device.data)
        iec61850.LinkedList_destroy(device_list)

        # discover all nodes
        [logical_nodes, error] = iec61850.IedConnection_getLogicalDeviceDirectory(
            con, gvar.iec_values["LD_name"])
        logical_node = iec61850.LinkedList_getNext(logical_nodes)
        gvar.iec_values["LN_name"] = iec61850.toCharP(logical_node.data)
        while logical_node:
            [ln_objects, error] = iec61850.IedConnection_getLogicalNodeVariables(
                con, gvar.iec_values["LD_name"]+"/"+iec61850.toCharP(logical_node.data))
            # ln_objects dont need to be iterated
            logical_node = iec61850.LinkedList_getNext(logical_node)

            # clean up
        iec61850.LinkedList_destroy(logical_node)
        iec61850.LinkedList_destroy(logical_nodes)

def check_config_every_five_s(con, nr):
    ''' check configRev every 5 seconds'''
    check_if_conf_changed(con, nr)
    time.sleep(5)


def test_client(ip, nr):
    ''' Main function for connecting to IEC61850 Server  '''

    gvar.completionTime = time.time() + 3600  # 3600s = 1h | 50s tollerance 

    con = iec61850.IedConnection_create()
    error = iec61850.IedConnection_connect(con, ip, int(os.environ.get('TCPPORT')))

    if error == iec61850.IED_ERROR_OK:
        # get configRev and if missmatch get complete model
        check_if_conf_changed(con, nr)
    else:
        print("Connection error")

    # check configRev every 5s
    #thread = threading.Thread(target=check_config_every_five_s, args=(con,nr))
    #thread.start()

    while True:
        if gvar.completionTime - time.time() <= 0:
            print(time.strftime("%H:%M:%S")+": Test Complete")
            iec61850.IedConnection_close(con)
            iec61850.IedConnection_destroy(con)
            os._exit(1)  # end program not only thread

        gvar.iec_values["remainingTime"] = str(
            round((gvar.completionTime - time.time()) / 60, 2)) + " Min left"

        if error == iec61850.IED_ERROR_OK:
            # Reading vars with Datasets
            # A data set in IEC 61850 is a list of variables that can be observed and transmitted together in a more efficient manner. Source: https://libiec61850.com/glossary/

            path = ["MMXU_MV$Trafo_DS_MMXU_MV", "MMXU_LV_1$Trafo_DS_MMXU_LV_1",
                             "MMXU_LV_2$Trafo_DS_MMXU_LV_2", "MMXU_LV_3$Trafo_DS_MMXU_LV_3"]
            
            data_set_path = [f"mallsensor{str(nr)}_Trafo/" + item for item in path]

            for path_to_data_set in data_set_path:

                if path_to_data_set not in gvar.dataset_structure:
                    [data_set_directory, error] = iec61850.IedConnection_getDataSetDirectory(
                        con, path_to_data_set, None)
                    # <iec61850.sLinkedList; proxy of <Swig Object of type 'LinkedList' at 0x7f5727f52120>>
                    gvar.dataset_structure[path_to_data_set] = iec61850.LinkedList_getNext(data_set_directory)
                    # Trafostation1_Trafo1/MMXU_LV_1.PhV.phsA.cVal[MX]
                
                data_set_dir = gvar.dataset_structure[path_to_data_set]

                [data_set_obj, error] = iec61850.IedConnection_readDataSetValues(
                    con, path_to_data_set, None)
                data_set_entrys = iec61850.ClientDataSet_getValues(
                    data_set_obj)

                # Debug:
                # print(data_set_obj)
                # Output: <Swig Object of type 'sClientDataSet *' at 0x7f5727f52900>
                # print(iec61850.ClientDataSet_getReference(data_set_obj))
                # Output: Trafostation1_Trafo1/MMXU_LV_1$Trafo1_DS_MMXU_LV_1
                # print(iec61850.MmsValue_getArraySize(data_set_entrys))
                # Output: 6 Elements

                while data_set_dir:
                    for i in range(iec61850.MmsValue_getArraySize(data_set_entrys)):
                        if iec61850.MmsValue_getElement(data_set_entrys, i) is not None:
                            if iec61850.MmsValue_getElement(iec61850.MmsValue_getElement(iec61850.MmsValue_getElement(data_set_entrys, i), 0), 0) is not None:
                                gvar.iec_values[iec61850.toCharP(data_set_dir.data)] = ": " + str(round(iec61850.MmsValue_toFloat(
                                    iec61850.MmsValue_getElement(iec61850.MmsValue_getElement(iec61850.MmsValue_getElement(data_set_entrys, i), 0), 0)), 2))

                            # TotVar TotW Hz one layer higher than e.g. PhV$phsA$cVal
                            # and iec61850.MmsValue_getElement(iec61850.MmsValue_getElement(iec61850.MmsValue_getElement(dataSetEntrys, i),0),0) == None:
                            elif iec61850.MmsValue_getElement(iec61850.MmsValue_getElement(data_set_entrys, i), 0) is not None:
                                gvar.iec_values[iec61850.toCharP(data_set_dir.data)] = ": " + \
                                    str(round(iec61850.MmsValue_toFloat(iec61850.MmsValue_getElement(
                                        iec61850.MmsValue_getElement(data_set_entrys, i), 0)), 2))
                    
                        data_set_dir = iec61850.LinkedList_getNext(data_set_dir)

                        

            print(time.strftime("%H:%M:%S")+": client ok")
        else:
            print(time.strftime("%H:%M:%S")+": Connection error")

        # let connection open
        time.sleep(60)
        #time.sleep(900) # 15min


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
