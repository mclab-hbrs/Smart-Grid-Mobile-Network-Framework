import random
import csv
from pathlib import Path

dataset = []

# Naming convention from IEC 61850 for all protocols
mmxu_devices = ["MMXU_MV","MMXU_LV_1","MMXU_LV_2","MMXU_LV_3"]
values = ["_A_phsA_f","_A_phsB_f","_A_phsC_f","_PhV_phsA_f","_PhV_phsB_f","_PhV_phsC_f"]

var_list_values = [dev+var for dev in mmxu_devices for var in values ]
# add keys for only MMXU_MV
var_list_values.extend(["MMXU_MV_TotW_f","MMXU_MV_TotVar_f","MMXU_MV_Hz_f"])


# how many data rows (mins) before the data repeats
row_count = int(input('How many sample values (rows/mins) do you need? \n'))

for i in range(row_count):
    iec_values = {}

    # Iterate through data vars
    for var in var_list_values:
        if "MMXU_MV_TotW_f" in var:
            iec_values["MMXU_MV_TotW_f"] =  round(5000.0 + random.randint(-3000,3000)/1000,2)
        if "MMXU_MV_TotVar_f" in var: 
            iec_values["MMXU_MV_TotVar_f"] =  round(200.0 + random.randint(-100,100)/1000,2)
        if "MMXU_MV_Hz_f" in var:
            iec_values["MMXU_MV_Hz_f"] =  round(50.0 + random.randint(-100,100)/1000,2)
        # Voltage
        if "PhV" in var:
            # Medium Voltage
            if "MMXU_MV" in var:
                iec_values[var] = round(69.0 + random.randint(-100,100)/1000,2)
            # Low Voltage
            else:
                iec_values[var] = round(12.0 + random.randint(-100,100)/1000,2)
        elif "A_phs" in var:
            # Medium Voltage
            if "MMXU_MV" in var:
                iec_values[var] = round(30.0 + random.randint(-100,100)/1000,2)
            else:
                iec_values[var] =  round(9.0 + random.randint(-10,10)/100,2)

    # add only values to dataset
    dataset.append(list(iec_values.values()))

with open('sample_data.csv', 'w', newline ='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',')
    csv_writer.writerow(var_list_values)
    csv_writer.writerows(dataset)