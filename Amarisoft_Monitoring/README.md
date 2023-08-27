# Doku
lteenb-2022-06-18.pdf

"The statistics sampling time is defined by delay between two calls within the same
connection. To get relevant statistics, you may let the WebSocket connected and call this API
regularly."

## API documentation
Abbreviations:
```
CCE - Control Channel Element
TTI - Transmission Time Interval
GBR - Guaranteed Bit Rate
GTP - GPRS Tunneling Protocol
RMS - Root Mean Square
RNTI - Radio Network Temporary Identifier
E-RAB - E-UTRAN Radio Access Bearer
CQI - Channel Quality Indicator
QCI - QoS Class Identifier
RNTI - Radio Network Temporary Identifier
```

Values returned during a `stats` retrieval:

### General information:
JSON Key        |  Typ             | Description
--------------- | ---------------- | --------------------------------------------------------------------- 
cpu             | Object           | Each member name defines a type and its value cpu load in % of one core.
instance_id     | Number           | Constant over process lifetime. Changes on process restart.
gtp_tx_bitrate  | Optional Number  | This field will be filled when multiple calls on the same socket are done, represents GTP payload bitrate (bits/seconds)
gtp_rx_bitrate  | Optional Number  | sent to core network and is equivalent to IP traffic. The bitrate is computed using the delay between two calls.
rf_ports        | Object           | Each member name is the RF port ID and each value is an object representing the TX-RX latency statistics (average, max and min values).
samples         | Object           | tx & rx; rms, max, sat, count
duration        | Number           | Time elapsed in seconds since the last call to the stats API.

### Cell information:
JSON Key                |  Typ     | Description
------------------------| -------- | --------------------------------------------------------------------- 
dl_bitrate              | Number   | Downlink bitrate in bits per seconds at PHY layer level (Counts acknowledged transmissions).
ul_bitrate              | Number   | Uplink bitrate in bits per seconds at PHY layer level (Counts successful transmissions).
mbms_bitrate            | Number   | Broadcast downlink bitrate in bits per seconds. 
dl_tx                   | Integer  | Number of downlink transmitted transport blocks (without retransmissions).
ul_tx                   | Integer  | Number of received uplink transport blocks (without CRC error).
dl_err                  | Integer  | Number of non transmitted downlink transport blocks (after retransmissions).
ul_err                  | Integer  | Number of non received uplink transport blocks (after retransmissions).
dl_retx                 | Integer  | Number of downlink retransmitted transport blocks.
ul_retx                 | Integer  | Number of received uplink transport blocks with CRC errors.

### Scheduling information (part of the cell object):
JSON Key                |  Typ     | Description
------------------------| -------- | --------------------------------------------------------------------- 
dl_sched_users_min      | Number   | Minimum downlink scheduled users per TTI.
dl_sched_users_avg      | Number   | Average downlink scheduled users per TTI.
dl_sched_users_max      | Number   | Maximum downlink scheduled users per TTI.
ul_sched_users_min      | Number   | Minimum uplink scheduled users per TTI.
ul_sched_users_avg      | Number   | Average uplink scheduled users per TTI.
ul_sched_users_max      | Number   | Maximum uplink scheduled users per TTI
dl_use_min              | Number   | Number between 0 and 1. Minimum downlink usage ratio, based on number of allocated resource blocks.
dl_use_avg              | Number   | Number between 0 and 1. Average downlink usage ratio, based on number of allocated resource blocks.
dl_use_max              | Number   | Number between 0 and 1. Maximum downlink usage ratio, based on number of allocated resource blocks.
ul_use_min              | Number   | Number between 0 and 1. Minimum uplink usage ratio, based on number of allocated resource blocks.
ul_use_avg              | Number   | Number between 0 and 1. Average uplink usage ratio, based on number of allocated resource blocks.
ul_use_max              | Number   | Number between 0 and 1. Maximum uplink usage ratio, based on number of allocated resource blocks.
ctrl_use_min            | Number   | Number between 0 and 1. Minimum control usage ratio, based on number of used CCE.
ctrl_use_avg            | Number   | Number between 0 and 1. Average control usage ratio, based on number of used CCE.
ctrl_use_max            | Number   | Number between 0 and 1. Maximum control usage ratio, based on number of used CCE.

### UE Information (part of the cell object):
JSON Key                |  Typ     | Description
------------------------| -------- | --------------------------------------------------------------------- 
ue_count_min            | Integer  | Minimum number of UE contexts.
ue_count_avg            | Integer  | Average number of UE contexts.
ue_count_max            | Integer  | Maximum number of UE contexts.

### Radio Bearer (part of the cell object):
JSON Key                |  Typ     | Description
------------------------| -------- | ---------------------------------------------------------------------
erab_count_min          | Integer  | Minimum number of established radio bearer. Applicable to LTE or NB-IoT cells.
erab_count_avg          | Integer  | Average number of established radio bearer. Applicable to LTE or NB-IoT cells.
erab_count_max          | Integer  | Maximum number of established radio bearer. Applicable to LTE or NB-IoT cells.
drb_count_min           | Integer  | Minimum number of established radio bearer. Applicable to NR cells.
drb_count_avg           | Integer  | Average number of established radio bearer. Applicable to NR cells.
drb_count_max           | Integer  | Maximum number of established radio bearer. Applicable to NR cells.

### Guaranteed bit rate information (part of the cell object):
JSON Key                |  Typ            | Description
------------------------| --------------- | ---------------------------------------------------------------------
dl_gbr_use_min          | Optional number | Minimum downlink GBR usage ratio. Not present for NB-IoT cells.
dl_gbr_use_avg          | Optional number | Average downlink GBR usage ratio. Not present for NB-IoT cells.
dl_gbr_use_max          | Optional number | Maximum downlink GBR usage ratio. Not present for NB-IoT cells.
ul_gbr_use_min          | Optional number | Minimum uplink GBR usage ratio. Not present for NB-IoT cells.
ul_gbr_use_avg          | Optional number | Average uplink GBR usage ratio. Not present for NB-IoT cells.
ul_gbr_use_max          | Optional number | Maximum uplink GBR usage ratio. Not present for NB-IoT cells.

Values returned with a `ue_get` retrieval:
### UE information (ue_list):
JSON Key        |  Typ             | Description
--------------- | ---------------- | --------------------------------------------------------------------- 
time            | Integer          | Time in seconds since eNB starting.
enb_ue_id       | Optional integer | eNB UE id. Present for LTE or NB-IoT UEs.
ran_ue_id       | Optional integer | RAN UE id. Present for NR UEs.
mme_ue_id       | Optional integer | MME UE id. It is present when the UEassociated logical S1-connection is setup.
amf_ue_id       | Optional integer | AMF UE id. It is present when the UEassociated logical NG-connection is setup.
linked_enb_ue_id| Optional integer | eNB UE id associated with the current NR UE for NSA.
linked_ran_ue_id| Optional integer | RAN UE id associated with the current LTE UE for NSA.
rnti            | Integer          | RNTI

### Cell information (ue_list):
JSON Key        |  Typ             | Description
--------------- | ---------------- | --------------------------------------------------------------------- 
cell_id         | Number           | Cell ID.
cqi             | Number           | Last reported CQI (Channel Quality Indicator).
ri              | Number           | Last reported rank indicator.
dl_bitrate      | Number           | Downlink bitrate in bits per seconds at PHY layer level (Counts acknowledged transmissions).
ul_bitrate      | Number           | Uplink bitrate in bits per seconds at PHY layer level (Counts successful transmissions).
dl_tx           | Integer          | Number of downlink transmitted transport blocks (without retransmissions).
ul_tx           | Integer          | Number of received uplink transport blocks (without CRC error).
dl_retx         | Integer          | Number of downlink retransmitted transport blocks.
ul_retx         | Integer          | Number of received uplink transport blocks with CRC errors.
dl_mcs          | Number           | Average downlink MCS.
ul_mcs          | Number           | Average uplink MCS.
turbo_decoder_min | Optional number| Minimum turbo/ldpc decoder pass.
turbo_decoder_avg | Optional number| Average turbo/ldpc decoder pass.
turbo_decoder_max | Optional number| Maximum turbo/ldpc decoder pass.
pucch1_snr      | Optional number  | PUCCH snr.
pusch_snr       | Optional number  | Last received PUSCH snr.
epre            | Optional number  | Last received EPRE in dBm.
ul_phr          | Optional number  | Last received power headroom report. To retrieve the value in dB, refer to 3GPP 36.133 table 9.1.8.4.
ul_path_loss    | Optional number  | Last computed UL path loss in dB, estimated from PHR.
p_ue Optional   | number           | UE transmission power in dB, estimated from PHR and Pmax set in the cell and reported by UE.
initial_ta      | Optional number  | Last timing advance measured with PRACH, expressed in unit of TS.

### E-UTRAN Radio Access Bearer Information (ue_list/erabs):
JSON Key        |  Typ             | Description
--------------- | ---------------- | --------------------------------------------------------------------- 
erab_id         | Number           | Radio bearer ID.
qci             | Number           | Radio beader QCI.
dl_total_bytes  | Integer          | Total downlink PDCP SDU byte count.
ul_total_bytes  | Integer          | Total uplink PDCP SDU byte count.