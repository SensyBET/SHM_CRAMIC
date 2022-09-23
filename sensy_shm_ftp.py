import tkinter as tk
from tkinter import filedialog
import sys
import os
import webbrowser
import subprocess
import signal
import pandas as pd
# from ftp_client import main as main_ftp
from binary_decoder import convert
from convert_csv_to_xl import convert_csv_xls

p = ""
b = ""

PINGADRR = {
    "Host" :"192.168.3.100",
    "Cabin 1" :"192.168.3.102",
    "Cabin 2" :"192.168.3.103",
    "Arduino 1" :"192.168.3.104",
    "Arduino 2" :"192.168.3.107"
}

downloading = 0

def __ping_everything():

    for ping in PINGADRR:
        if __ping(PINGADRR[ping]) == True:
            print(f"{ping} is responding to ping request")
        else: 
            print(f"{ping} is NOT responding to ping request")

def __ping(host):
    response = os.system("ping " + host)
    if response == 0:
        return True
    else:
        return False    

def __open_browser():
    webbrowser.open(PINGADRR["Arduino 1"])
    webbrowser.open(PINGADRR["Arduino 2"])
    print("Click ON/OFF buttton to reset (Both Tab)")

def __select_file():
    
    # path= filedialog.askdirectory(title="Select a Folder")
    path= filedialog.askopenfilename(title="Select a File", filetype=(('all files','*.*'),))
    return path

def __select_folder():
    
    # path= filedialog.askdirectory(title="Select a Folder")
    path= filedialog.askdirectory(title="Select a Directory")
    return path

def __convert_to(file):
    print("Covnerting file: %s" % file)
    convert(file)

def __mass_convert(folder):
    print("Mass converting %s" % folder)
    for path in os.listdir(folder):
        if path[-4:] == '.bin':
            __convert_to(f"{folder}/{path}")
    print("Merging everything")

    csv_list = []
    for path in os.listdir(folder):
        if path[-4:] == '.csv':
            csv_list.append(f"{folder}/{path}")
            print(csv_list)

    combined_csv = pd.concat([pd.read_csv(f) for f in csv_list ])
    combined_csv.to_csv( f"{folder}/MERGE_DATA.csv", index=False, encoding='utf-8-sig')
    print(f"Merging file created as :{folder}/MERGE_DATA.csv")

def __convert_csv(file):
    print("Covnerting file: %s" % file)
    convert_csv_xls(file)

def __ftp_request():
    #main_ftp()
    global downloading
    global p, b
    if downloading == 0:
        p = subprocess.Popen(['python', 'ftp_client1.py'], start_new_session=True)
        b = subprocess.Popen(['python', 'ftp_client2.py'], start_new_session=True)
        downloading = 1
    else:
        downloading = 0
        p.kill()
        b.kill()
        print("CABIN1 AND CABIN2 subprocess have been killed")


def main():
    mainwindow = tk.Tk()
    mainwindow.title("Cramic Downloader")
    mainwindow.iconbitmap("assets/img/crane.ico")
    mainwindow.resizable(width=False, height=False)

    button = tk.Button(
            mainwindow,
            text="Download",
            foreground="white",
            background="grey",
            width=10,
            height=2,
            command=lambda:__ftp_request()
            )
    button2 = tk.Button(
            mainwindow,
            text="Ping",
            foreground="white",
            background="black",
            width=10,
            height=1,
            command=lambda:__ping_everything()
            )
    button3 = tk.Button(
            mainwindow,
            text="Reset",
            foreground="white",
            background="black",
            width=10,
            height=1,
            command=lambda:__open_browser()
            )

    button4 = tk.Button(
            mainwindow,
            text="Convert file",
            foreground="white",
            background="grey",
            width=10,
            height=2,
            command=lambda:__convert_to(__select_file())
            )    

    button5 = tk.Button(
            mainwindow,
            text="CSV to XLS",
            foreground="white",
            background="grey",
            width=10,
            height=2,
            command=lambda:__convert_csv(__select_file())
            ) 

    button6 = tk.Button(
            mainwindow,
            text="Mass Convert",
            foreground="white",
            background="grey",
            width=10,
            height=2,
            command=lambda:__mass_convert(__select_folder())
            )      

    tk.Label(mainwindow, width=30, text="CRAMIC DATALOGGER", font='Helvetica 28 bold').grid(row=0, column=0, columnspan=2, pady=20) 
    
    button.grid(row=1, column=1, pady=5)
    tk.Label(mainwindow, width=30, text="Download data from datalogger", font=12).grid(row=1, column=0) 
    
    button2.grid(row=2, column=1, pady=5)
    tk.Label(mainwindow, width=30, text="Ping everything", font=12).grid(row=2, column=0)
    
    button3.grid(row=3, column=1, pady=5)
    tk.Label(mainwindow, width=30, text="Open both reset menu", font=12).grid(row=3, column=0)
    
    button4.grid(row=4, column=1, pady=5)
    tk.Label(mainwindow, width=30, text="Convert data to readable format", font=12).grid(row=4, column=0)

    button6.grid(row=5, column=1, pady=5)
    tk.Label(mainwindow, width=30, text="Mass convert data to readable format", font=12).grid(row=5, column=0)

    button5.grid(row=6, column=1, pady=5)
    tk.Label(mainwindow, width=30, text="Convert .csv to xls format", font=12).grid(row=5, column=0)

    mainwindow.mainloop()

if __name__ == '__main__':
    main()

    