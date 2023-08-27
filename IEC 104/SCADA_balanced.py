'''Programm for connecting to an IEC 104 Slave, e.g. a Substation.'''
import os
import threading
import time

from lib60870 import lib60870
from lib60870.lib60870 import IEC60870ConnectionEvent, CauseOfTransmission
from lib60870.T104Connection import T104Connection
from lib60870.information_object import ClockSynchronizationCommand, InformationObject, SingleCommand

# lib for RESTfull API
from flask import Flask, request, render_template, redirect


class gvar():
    # Content Array
    iec_values = {}

    # time the experiment is over
    completionTime = 0


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

    for ip in array:
        thread = threading.Thread(target=test_client,args=(ip,))
        thread.start()
    return redirect("/", code=302)

# Only the controlling station sends the STARTDT. The expected mode of operation is that the STARTDT is sent only once after the initial establishment of the connection.
# The connection then operates with both controlled and controlling station permitted to send any message at any time until the controlling station decides to close the
# connection with a STOPDT command. / Source: "Description and analysis of IEC 104 Protocol" p.12

# function to handle connection events


def connection_handler(parameters, event):
    ''' function to handle connection events'''
    if event == IEC60870ConnectionEvent.IEC60870_CONNECTION_CLOSED:
        print("Disconnected")
    elif event == IEC60870ConnectionEvent.IEC60870_CONNECTION_OPENED:
        print("Connected")
    elif event == IEC60870ConnectionEvent.IEC60870_CONNECTION_STARTDT_CON_RECEIVED:
        print("StartDT con received")
    elif event == IEC60870ConnectionEvent.IEC60870_CONNECTION_STOPDT_CON_RECEIVED:
        print("StopDT con received")


def asdu_received_handler(asdu):
    '''function that is called on incoming messages'''
    for element in asdu.get_elements():
        try:
            gvar.iec_values[str(element.get_object_address())] = element.get_value()
        except AttributeError:
            pass
    return True


# == Sending a read request
# The IEC 60870 documents don't recommend this service (cyclical data requests or polling) but it is an easy way to get the required data. You just need to know the common address (CA) and the information object address (IOA) to create the proper request.
#   con.SendReadCommand(1 /* CA */, 2001 /* IOA */);
# The call is non-blocking. You have to evaluate the response in the ASDUReceivedHandler callback function.
# Typically it is expected that the server response contains only the basic data type without timestamps (that is using the message types for a specific data type that does not contain the timestamps)!

# == Interrogation
# You can also request a group of data items from a slave with a single request. On the master (client) side you can simply use the SendInterrogationCommand method of the Connection object:
# con.SendInterrogationCommand (CauseOfTransmission.ACTIVATION, 1, 20);


# Function for connecting to IEC104 Server
def test_client(ip):
    ''' Main function for connecting to IEC 104 Slave '''

    gvar.completionTime = time.time() + 3600  # 3600s = 1h

    print("start connecting")
    client = T104Connection(ip.encode('UTF-8'), int(os.environ.get('TCPPORT')))
    client.set_connection_handler(connection_handler)
    client.set_asdu_received_handler(asdu_received_handler)

    with client.connection():
        client.send_start_dt()
        # Request Set of Data from Station with Common Address 1 / C_IC_NA_1(100) Interrogation command
        client.send_interrogation_command(ca=1)

        # The direct operate command procedure and the select before operate command procedure.
        # To send a command for the direct operate command procedure you have to send an ACTIVATION APDU to the outstation.
        # public SingleCommand (int ioa, bool command, bool selectCommand, int qu) The qualifier (qu) should in general be set to 0.
        # con.SendControlCommand (TypeID.C_SC_NA_1, CauseOfTransmission.ACTIVATION, 1, new SingleCommand (5000, true, false, 0));

        # activates spontaneous transmissions
        # Activation start data transfer -> Answer from Substation: activation confirmation, activation termination when finished
        client.send_control_command(
            cot=CauseOfTransmission.ACTIVATION, ca=1, command=SingleCommand(5000, True, False, 0))

        while True:
            if gvar.completionTime - time.time() <= 0:
                # clock sync closes the connection, unable to add timestamp like in C doc
                # CP56Time2a currentTime = new CP56Time2a (DateTime.Now);
                # con.SendClockSyncCommand (1 /* CA */, currentTime);

                client.send_clock_sync_command(ca=1)
                print(time.strftime("%H:%M:%S")+": Test Complete")
                os._exit(1)  # end program not only thread

            gvar.iec_values["remainingTime"] = str(
                round((gvar.completionTime - time.time()) / 60, 2)) + " Min left"

            time.sleep(60)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
