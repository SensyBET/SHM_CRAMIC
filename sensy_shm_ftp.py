import tkinter as tk
from tkinter import filedialog
import sys
import os
import webbrowser
import subprocess
import signal
# from ftp_client import main as main_ftp
from binary_decoder import convert

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

def __convert_to(file):
    print("Covnerting file: %s" % file)
    convert(file)

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

    tk.Label(mainwindow, width=30, text="CRAMIC DATALOGGER", font='Helvetica 28 bold').grid(row=0, column=0, columnspan=2, pady=20) 
    button.grid(row=1, column=1, pady=5)

    tk.Label(mainwindow, width=30, text="Download data from datalogger", font=12).grid(row=1, column=0) 
    button2.grid(row=2, column=1, pady=5)

    tk.Label(mainwindow, width=30, text="Ping everything", font=12).grid(row=2, column=0)
    button3.grid(row=3, column=1, pady=5)

    tk.Label(mainwindow, width=30, text="Open both reset menu", font=12).grid(row=3, column=0)
    button4.grid(row=4, column=1, pady=5)

    tk.Label(mainwindow, width=30, text="Convert data to readable format", font=12).grid(row=4, column=0)

    mainwindow.mainloop()

if __name__ == '__main__':
    main()

    