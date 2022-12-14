# version: 1.2
# 
# from 1.0 -> 1.1
# - add retrieve_new_files, called every 30 s
# - add port_number in global variables
# from 1.0 -> 1.1
# - adapted to firmware 1.2: retrieve data every 60 sec, change FTP credential
# - improve FTP download

from ftplib import FTP
from datetime import timedelta
import datetime
import os
import time, traceback
import signal
import sys


#global variable
RETRIEVER_PERIOD_IN_S = 60
if 0:
    serial_id = "CABIN1"##20510031
    # hostname = "M" + str(serial_id)
    hostname = "192.168.3.102" # public IP or local IP
else:
    serial_id = "CABIN2"##20510031
    hostname = "192.168.3.103" # public IP or local IP
port_number = 21
d = datetime.datetime.utcnow() + datetime.timedelta(0, -10)
local_folder = "data_sensy\\" + str(serial_id) + "\\data_{:02d}_{:02d}_{:02d}_{:02d}{:02d}{:02d}".format(d.year, d.month, d.day, d.hour, d.minute, d.second)
ftp = 0
latest_name = None

# periodic task
def every(delay, task):
  next_time = time.time() + delay
  while True:
    time.sleep(max(0, next_time - time.time()))
    try:
      task()
    except Exception:
      traceback.print_exc()
      # in production code you might want to have this instead of course:
      # logger.exception("Problem while executing repetitive task.")
    # skip tasks if we are behind schedule:
    next_time += (time.time() - next_time) // delay * delay + delay

#d = date.now(timezone.utc)
def get_curr_filename(d):
    filename = "ACC_{:02d}_{:02d}_{:02d}_{:02d}{:02d}{:02d}.BIN".format(d.year, d.month, d.day, d.hour, d.minute, d.second)
    return filename

def print_time():
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S.%f")[:-3])

def retrieve_one_file():
    global ftp
    global d

    d = d + datetime.timedelta(0, +1)

    filename = get_curr_filename(d)
    t1 = time.time()
    with open(local_folder + "\\" + filename, 'wb') as local_file:
        ftp.retrbinary('RETR '+ filename, local_file.write)
    t2 = time.time()
        
    print("{} retrieved in {:.3f} seconds".format(filename, t2 - t1))

def retrieve_new_files():
    global ftp
    global latest_name

    t1 = time.time()

    cnt = 0
    filename_list = list()
    lines = []
    ftp.dir("", lines.append)

    # list with new valid filename
    for line in lines:
        tokens = line.split(maxsplit = 9)
        cur_filename = tokens[3]
        cur_filesize = int(tokens[2])
        if cur_filesize > 0 and (latest_name is None or cur_filename > latest_name):
            filename_list.append(cur_filename)
        
    filename_list.sort()

    # first attempt, get only one file
    if latest_name is None:
        filename_list = [filename_list.pop()]

    print("filename_list=", filename_list)       
    #exit()

    for cur_filename in filename_list:  
        if latest_name is None or (cur_filename > latest_name):
            try:
                with open(local_folder + "\\" + cur_filename, 'wb') as local_file:
                    ftp.retrbinary('RETR '+ cur_filename, local_file.write)
                latest_name = cur_filename
                cnt = cnt+1
            except:
                print("error with{}".format(cur_filename))
    
    t2 = time.time()
    
    print("{} files retrieved in {:.3f} seconds (last={})".format(cnt, t2 - t1, latest_name))
        

def signal_handler(sig, frame):
    print("FTP client: end")
    sys.exit(0)

def main():
    global ftp 
    print("FTP client: start")
    
    signal.signal(signal.SIGINT, signal_handler)

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
    print("Folder {} created".format(local_folder))


    print("FTP hostname={} port={}".format(hostname, port_number))
    #ftp = FTP(host=hostname, user='shm', passwd='woelfel')
    ftp = FTP()
    ftp.connect(host=hostname, port=port_number, timeout=5)
    print("FTP connect OK")
    if 0: 
        ftp.login(user='shm', passwd='woelfel')
    else:
        ftp.login(user='shm_dau', passwd='Woelfel15')
    print("FTP login OK")
    
    #every(1, retrieve_one_file) //old

    

    retrieve_new_files()
    every(RETRIEVER_PERIOD_IN_S, retrieve_new_files)

    # while True:
    #     pass

if __name__ == "__main__":
    main()