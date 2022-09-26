# version: 1.2

import struct
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET
import json


FIRMWARE_VERSION = "RELEASE_1_2" #"TEST_CALIB"

if 1:
    # FOLDER_MEASUREMENT       = "data_sensy\\CABIN1\\data_2022_08_22_144126"
    FILENAME_MONITOR_CONFIG  = "config\\default\\monitor_user_settings.xml"
    FILENAME_MONITOR_SCALING = "config\\default\\monitor_scaling.txt"
    FILENAME_SENSOR_CONFIG    = "config\\sensy\\sensor_config_M22510023.json"
else:
    # FOLDER_MEASUREMENT       = "data_sensy\\CABIN2\\data_2022_09_09_094901"
    FILENAME_MONITOR_CONFIG  = "config\\default\\monitor_user_settings.xml"
    FILENAME_MONITOR_SCALING = "config\\default\\monitor_scaling.txt"
    FILENAME_SENSOR_CONFIG    = "config\\sensy\\sensor_config_M22510024.json"

# Constants
VERBOSE = 0
N_CHANNEL = 24
BLOCK_SIZE_MAX = (N_CHANNEL + 2) * 4
TICK_MAX = 250 #sampling rate
SEPARATOR = ","
FORCE_OVERWRITE = True
# Resolution
ADC_RESOL_IN_V = 5.0 / ((2**24) - 1)
# decoding phase
PH_0_INIT = 0 # init value
PH_1_TS1  = 1 # decode timestamp1
PH_2_TS2  = 2 # decode timestamp2
PH_3_DATA = 3 # decode adc data value
# CSV output
CSV_NB_LINE_MAX = 500000 # max=1048576


file_idx = 0

# print iaw verbosity
def debug_print(v, *args):
    """Debug print"""
    if VERBOSE >= v:
        print(*args)


def create_new_output_file (filename, header):
    global file_idx
    print("header:")
    print(header)
    # Create output file
    output_file_name = filename[:-3] + "csv"
    print(output_file_name)

    if os.path.exists(output_file_name):
        print("FORCE_OVERWRITE")
        new_file = open(output_file_name, "w")

    else:
        new_file = open(output_file_name, "x")
    print("{} created".format(output_file_name))
    
    file_idx = file_idx +1

    # Write header
    new_file.write(header)

    return new_file

def convert(filename):
    """Convert functoion !!! NEED cleaning !!!"""
    print("N_CHANNEL={} BLOCK_SIZE_MAX={}".format(N_CHANNEL, BLOCK_SIZE_MAX))

    ### Load Scaling Config ###
    print("FILENAME_MONITOR_SCALING={}".format(FILENAME_MONITOR_SCALING))
    scaling_file = open(FILENAME_MONITOR_SCALING, 'r')
    scaling_lines = scaling_file.readlines()
    monitor_scaling_array = list()
    idx = 0
    for line in scaling_lines:
        a = line.strip().split(";")
        try:
            if (idx+1) == int(a[0]):
                monitor_scaling_array.append({
                    "adc_gain": float(a[1]),
                    "adc_offs": float(a[2])
                })
            idx += 1
        except:
            pass
    debug_print(1, "monitor_scaling_array=", monitor_scaling_array)

    ### Load Monitor Config ###
    print("FILENAME_MONITOR_CONFIG={}".format(FILENAME_MONITOR_CONFIG))
    doc = minidom.parse(FILENAME_MONITOR_CONFIG)
    # Write timestamp in file
    TSLOGOn = int(doc.getElementsByTagName('TSLog_mode')[0].firstChild.nodeValue)
    # Down sampling rate
    LogDownSRate = list()
    for x in doc.getElementsByTagName("downSRate")[0].getElementsByTagName('unsignedShort'):
        # print(x.firstChild.nodeValue)
        LogDownSRate.append(int(x.firstChild.nodeValue))
    # Log Priority
    LogPriority = list()
    for x in doc.getElementsByTagName("logPriority")[0].getElementsByTagName('byte'):
        LogPriority.append(int(x.firstChild.nodeValue))
    debug_print(2, "TSLOGOn={}".format(TSLOGOn))
    debug_print(1, "Channel Config")
    for i in range(0, N_CHANNEL):
        debug_print(1, "CH{:02d}: LogDownSRate={:2d}, logPriority={:2d}".format(
            i+1, LogDownSRate[i], LogPriority[i]))


    ### Load Monitor Config ###
    print("FILENAME_SENSOR_CONFIG={}".format(FILENAME_SENSOR_CONFIG))
    json_sensor_config = open(FILENAME_SENSOR_CONFIG)
    dict_sensor_config = json.load(json_sensor_config)
    array_sensors_scaling = dict_sensor_config["sensor_scaling"]

    array_sensor_scaling = list()

    for i in range(0, N_CHANNEL):
        try:
            res = [x for x in dict_sensor_config['sensor_scaling'] if x['channel_idx'] == (i+1)]
            # res.pop('channel_idx')
            # print(i, res)
            array_sensor_scaling.append(res[0])
        except:
            tmp = dict_sensor_config['sensor_scaling_default'].copy()
            # tmp["channel_idx"] = (i+1)
            array_sensor_scaling.append(tmp)

    for i in range(0, N_CHANNEL):
        x = array_sensor_scaling[i]
        debug_print(1, i, x['name'], x['sensor_gain'], x['sensor_offs'])


    # Define channel order based on LogPriority
    LogChanSortedSize = 0
    LogChanSorted = list()
    for priority in range(0, N_CHANNEL):
        for chidx in range (0, N_CHANNEL):
            if (LogPriority[chidx] == priority):
                # LogChanSorted[LogChanSortedSize] = chidx
                LogChanSorted.append(chidx)
                LogChanSortedSize += 1
    debug_print(1, "LogChanSortedSize=", LogChanSortedSize)
    debug_print(1, "LogChanSorted=", LogChanSorted)
    print(LogChanSortedSize)
    # Initialize header
    if (TSLOGOn):
        header = "time (ms)"
    else:
        header = ""
    for prio_idx in range(0, LogChanSortedSize):
        ch_idx = LogChanSorted[prio_idx]
        header += SEPARATOR + "CH{:02d}".format(ch_idx+1, )
        header += " ({})".format(array_sensor_scaling[ch_idx]['name'])
        header += " p={}".format(LogPriority[ch_idx])
        header += " DS={}".format(LogDownSRate[ch_idx])
    header += "\n"
    print(header)
    cv_file_path = create_new_output_file(filename, header)
    line_cnt = 0

    ts = 0.0

    with open(filename, 'rb') as file:

        eof_reached = False
        data = list()
        TimeIdx = 1 #[1;250]
        phase = PH_0_INIT
        prio_idx = 0
        ch_cnt = 0

        # decode header
        if FIRMWARE_VERSION == "RELEASE_1_2":
            nheader = file.read(2)
            nmod = file.read(2)
            nch = file.read(2)
            nch_acc  = file.read(2)
            nch_temp = file.read(2)
            fs = file.read(2)
            nbuff = file.read(2)
            header_vers_main = file.read(2)
            header_vers_sub = file.read(2)

        while not eof_reached:
            data_bytes = file.read(4)
            if len(data_bytes) < 4:
                eof_reached = True
                break
            
            debug_print(2, "TimeIdx={}, ph={} ch_cnt={} prio_idx={}".format(TimeIdx, phase, ch_cnt, prio_idx))
            if (phase == PH_0_INIT): #init
                prio_idx = 0
                ch_cnt = 0
                data = list()
                # next
                if (TSLOGOn == 0):
                    phase = PH_3_DATA # skip timestamp decoding
                else:
                    phase = PH_1_TS1

            debug_print(2, "TimeIdx={}, ph={} ch_cnt={} prio_idx={}".format(TimeIdx, phase, ch_cnt, prio_idx))
            if (phase == PH_0_INIT): #init
                prio_idx = 0
                ch_cnt = 0
                data = list()
                # next
                if (TSLOGOn == 0):
                    phase = PH_3_DATA # skip timestamp decoding
                else:
                    phase = PH_1_TS1

            if (phase == PH_1_TS1): #decode timestamp1
                ts1 = struct.unpack('I', data_bytes)[0] #seconds
                phase = PH_2_TS2
            elif (phase == PH_2_TS2): #decode timestamp2
                ts2 = struct.unpack('I', data_bytes)[0] #ticks [0; 249]
                #ts_s = (str(ts1) + ".{:03d}").format(int(1000*ts2/TICK_MAX))
                ts = ts_ms = (str(ts1) + "{:03d}").format(int(1000*ts2/TICK_MAX))
                phase = PH_3_DATA
            else: # decode adc value
                adc_val = struct.unpack('i', data_bytes)[0]


                #get net ch_idx to decode
                ch_found = False
                while (not ch_found and prio_idx < LogChanSortedSize):
                    ch_idx = LogChanSorted[prio_idx]
                    ch_dsrate = LogDownSRate[ch_idx]
                    if (ch_dsrate == 0 or (TimeIdx % ch_dsrate) != 0):
                        data.append("")
                    else:
                        # convention
                        # vsens[V]            = (adc_val[ADC] - adc_ofs[ADC]) * adc_gain[V/ADC]",
                        # meas [sensor_unit]  = vsens[V] * sensor_gain[sensor_unit/V] + sensor_offs[sensor_unit]"
                        vsens = (adc_val - monitor_scaling_array[ch_idx]["adc_offs"]) * monitor_scaling_array[ch_idx]["adc_gain"]
                        meas = (vsens - array_sensor_scaling[ch_idx]["sensor_offs"]) *  array_sensor_scaling[ch_idx]["sensor_gain"]
                        data.append(meas)
                        ch_found = True
                    # print("prio_idx={}, ch_idx={}, dsrate={}: result={}".format(prio_idx, ch_idx, ch_dsrate, ch_found))
                    prio_idx += 1
                    ch_cnt +=1

                if not ch_found:
                    print("ERROR")
                    exit() #TODO-ONG throw exception

            if ch_cnt >= N_CHANNEL:
                str_data = str(ts) + SEPARATOR + SEPARATOR.join(str(x) for x in data) + "\n"
                cv_file_path.write(str_data)
                debug_print(2,"{} : {}".format(TimeIdx, str_data))
                TimeIdx += 1
                line_cnt += 1
                phase = PH_0_INIT
    print("END")
