'''Programm representing an IEC 104 Slave, e.g. a Substation.'''
import csv
import logging
import random
import time

from lib60870 import lib60870
from lib60870.lib60870 import IEC60870ConnectionEvent, CauseOfTransmission, QualityDescriptor, TypeID
from lib60870.T104Slave import T104Slave
from lib60870.information_object import *
from lib60870.asdu import ASDU

logging.basicConfig(
    format='%(asctime)s %(name)s:%(levelname)s:%(message)s', level=logging.INFO)


class gvar():
    dataset = []
    dataset_index = 0
    spontaneous = False


def clock_sync_callback(parameter, connection, asdu, newtime):
    '''handler for timesync command'''
    print("Time sync command with time: " + str(newtime))
    return True


def connection_request_callback(parameter, conn):
    '''handler for new connection'''
    print("New connection from " + str(conn))
    return True


def add_information_ojects(asdu):
    '''function adding all values elements to asdu'''
    # M_SP_NA_1(1) Single point information (BOOLEAN)
    # M_ME_NB_1(11) Measured value, scaled value without time tag length = 3        Object type MeasuredValueScaled
    # M_ME_TB_1(12) Measured value, scaled value with CP56Time2a time tag length = 10
    # M_ME_NC_1(13) Short measured value (FLOAT32)
    # M_ME_TC_1(14) Short measured value (FLOAT32) with CP24Time2a
    # Use of M_ME_NC_1(13), because the IEC61850 test setup does not read the time stamps and these would be send with Interrogaten in IEC104

    asdu.add_information_object(MeasuredValueShort(100, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_TotW_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_TotW_f
    asdu.add_information_object(MeasuredValueShort(101, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_TotVar_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_TotVar_f
    asdu.add_information_object(MeasuredValueShort(102, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_Hz_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_Hz_f

    asdu.add_information_object(MeasuredValueShort(110, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_PhV_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_PhV_phsA_f
    asdu.add_information_object(MeasuredValueShort(111, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_PhV_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_PhV_phsB_f
    asdu.add_information_object(MeasuredValueShort(112, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_PhV_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_PhV_phsC_f

    asdu.add_information_object(MeasuredValueShort(120, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_A_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_A_phsA_f
    asdu.add_information_object(MeasuredValueShort(121, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_A_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_A_phsB_f
    asdu.add_information_object(MeasuredValueShort(122, float(
        gvar.dataset[gvar.dataset_index]["MMXU_MV_A_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU0_A_phsC_f

    # Low Voltage 1
    asdu.add_information_object(MeasuredValueShort(210, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_1_PhV_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_1_PhV_phsA_f
    asdu.add_information_object(MeasuredValueShort(211, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_1_PhV_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_1_PhV_phsB_f
    asdu.add_information_object(MeasuredValueShort(212, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_1_PhV_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_1_PhV_phsC_f

    asdu.add_information_object(MeasuredValueShort(220, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_1_A_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_1_A_phsA_f
    asdu.add_information_object(MeasuredValueShort(221, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_1_A_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_1_A_phsB_f
    asdu.add_information_object(MeasuredValueShort(222, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_1_A_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_1_A_phsC_f

    # Low Voltage 2
    asdu.add_information_object(MeasuredValueShort(310, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_2_PhV_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_2_PhV_phsA_f
    asdu.add_information_object(MeasuredValueShort(311, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_2_PhV_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_2_PhV_phsB_f
    asdu.add_information_object(MeasuredValueShort(312, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_2_PhV_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_2_PhV_phsC_f

    asdu.add_information_object(MeasuredValueShort(320, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_2_A_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_2_A_phsA_f
    asdu.add_information_object(MeasuredValueShort(321, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_2_A_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_2_A_phsB_f
    asdu.add_information_object(MeasuredValueShort(322, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_2_A_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_2_A_phsC_f

    # Low Voltage 2
    asdu.add_information_object(MeasuredValueShort(410, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_3_PhV_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_3_PhV_phsA_f
    asdu.add_information_object(MeasuredValueShort(411, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_3_PhV_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_3_PhV_phsB_f
    asdu.add_information_object(MeasuredValueShort(412, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_3_PhV_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_3_PhV_phsC_f

    asdu.add_information_object(MeasuredValueShort(420, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_3_A_phsA_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_3_A_phsA_f
    asdu.add_information_object(MeasuredValueShort(421, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_3_A_phsB_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_3_A_phsB_f
    asdu.add_information_object(MeasuredValueShort(422, float(
        gvar.dataset[gvar.dataset_index]["MMXU_LV_3_A_phsC_f"]), QualityDescriptor.IEC60870_QUALITY_GOOD))  # DO_MMXU_LV_3_A_phsC_f


def interrogation_callback(parameter, connection, asdu, qoi):
    '''handler for interrogation command'''
    print("Received interrogation for group " + str(qoi))

    # 20: interrogated by general interrogation / Source: "Description and analysis of IEC 104 Protocol" p.35
    if qoi == 20:
        connection.send_act_con(asdu)

        # Bool Values
        # new_asdu = ASDU(parameter, TypeID.M_SP_NA_1, False, CauseOfTransmission.INTERROGATED_BY_STATION, 0, 1)
        # new_asdu.add_information_object(SinglePointInformation(104, True, QualityDescriptor.IEC60870_QUALITY_GOOD))
        # new_asdu.add_information_object(SinglePointInformation(105, False, QualityDescriptor.IEC60870_QUALITY_GOOD))
        # connection.send_asdu(new_asdu)

        new_asdu = ASDU(parameter, TypeID.M_ME_NC_1, False,
                        CauseOfTransmission.INTERROGATED_BY_STATION, 0, 1)

        add_information_ojects(new_asdu)

        connection.send_asdu(new_asdu)

        connection.send_act_term(asdu)
    else:
        connection.send_act_con(asdu, True)
    return True


def asdu_callback(parameter, connection, asdu):
    '''handler for incomming messages and check if interrogation'''
    
    print("Received asdu " + str(asdu))
    if asdu.get_type_id() == TypeID.C_SC_NA_1:  # C_IC_NA_1(100) | Interrogation command
        print("received single command\n")
        sc = asdu.elements[0]
        if sc.get_object_address() == 5000:
            print("IOA: " + str(sc.get_object_address()) +
                  "switch to " + str(sc.get_state()))
            cot = CauseOfTransmission.ACTIVATION_CON
            gvar.spontaneous = True
        else:
            cot = CauseOfTransmission.UNKNOWN_INFORMATION_OBJECT_ADDRESS
        if asdu.get_cot() == CauseOfTransmission.ACTIVATION:
            pass
        else:
            cot = CauseOfTransmission.UNKNOWN_CAUSE_OF_TRANSMISSION
        asdu.set_cot(cot)
        connection.send_asdu(asdu)
        return True
    elif asdu.get_type_id() == TypeID.C_RD_NA_1:  # C_RD_NA_1(102) | Read command
        print("received read command\n")
        sc = asdu.elements[0]
        new_asdu = ASDU(parameter, TypeID.M_ME_NC_1, False,
                        CauseOfTransmission.ACTIVATION_CON, 0, 1)
        if sc.get_object_address() == 100:
            new_asdu.add_information_object(MeasuredValueShort(
                100, 5000.0 + random.randint(-3000, 3000)/1000, QualityDescriptor.IEC60870_QUALITY_GOOD))
        if sc.get_object_address() == 101:
            new_asdu.add_information_object(MeasuredValueShort(
                101, 200.0 + random.randint(-100, 100)/1000, QualityDescriptor.IEC60870_QUALITY_GOOD))
        if sc.get_object_address() == 102:
            new_asdu.add_information_object(MeasuredValueShort(
                102, 50.0 + random.randint(-100, 100)/1000, QualityDescriptor.IEC60870_QUALITY_GOOD))
        # ToDo: Add More
        connection.send_asdu(new_asdu)
        connection.send_act_term(asdu)
        return True
    else:
        return False


def main():
    ''' Main function for starting IEC 104 Slave '''

    # LIB60870-C: In the C version a server/slave is represented by the Slave data type.
    t104slave = T104Slave()
    # b"localhost") Bind to every IP
    t104slave.set_local_address(ip=b"0.0.0.0")
    # t104slave.MaxOpenConnections = 10
    # t104slave.set_local_port(2405)
    connection_parameters = t104slave.get_connection_parameters()

    # Set up callbacks
    t104slave.set_connection_request_handler(connection_request_callback)
    t104slave.set_clock_synchronization_handler(clock_sync_callback)
    t104slave.set_interrogation_handler(interrogation_callback)
    t104slave.set_asdu_handler(asdu_callback)

    # read dataset
    csv_reader = csv.DictReader(open('sample_data.csv'))
    for row in csv_reader:
        gvar.dataset.append(next(csv_reader))

    if not t104slave.start():
        raise RuntimeError("Server not started")

    try:
        while True:
            if gvar.spontaneous is True:
                # IEC 60870-5-104 Cyclic Transmission / Source: https://www.satec-global.com/sites/default/files/PM180-IEC-60870-5.pdf
                # In IEC 60870-5-104, configured cyclic data is transmitted periodically to the selected controlling station after it confirms start of data transfer.
                # An interrogation command interrupts cyclic transmission in progress, which is automatically restarted after the interrogation command has been responded.

                asdu = ASDU(connection_parameters, TypeID.M_ME_NC_1, False,
                            CauseOfTransmission.PERIODIC, 0, 1, False, False)
                add_information_ojects(asdu)
                t104slave.enqueue_asdu(asdu)

            if gvar.dataset_index + 1 >= len(gvar.dataset):
                gvar.dataset_index = 0
            else:
                gvar.dataset_index += 1

            time.sleep(60)
            #time.sleep(900) # 15min
    except KeyboardInterrupt:
        pass
    finally:
        t104slave.stop()


if __name__ == "__main__":
    main()
