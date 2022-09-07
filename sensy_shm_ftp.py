import tkinter as tk
import sys
import webbrowser
from ftp_client import main as main_ftp


class PrintLogger(): # create file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass

def __open_browser():
    webbrowser.open("https://192.168.3.104")
    webbrowser.open("https://192.168.3.107")

def main():
    mainwindow = tk.Tk()
    mainwindow.title("Cramic Downloader")
    mainwindow.iconbitmap("assets/img/crane.ico")

    button = tk.Button(
            mainwindow,
            text="Download",
            foreground="white",
            background="grey",
            width=10,
            height=2,
            command=lambda:main_ftp()
            )

    button2 = tk.Button(
            mainwindow,
            text="Reset",
            foreground="white",
            background="grey",
            width=10,
            height=2,
            command=lambda:__open_browser()
            )
            
    button.pack(side=tk.RIGHT, padx=5, pady=5)
    button2.pack(side=tk.RIGHT, padx=5, pady=5)
    console = tk.Text(mainwindow,width=60, height=30, background='ivory')
    console.pack(side=tk.LEFT, padx=5, pady=5)

    pl = PrintLogger(console)

    sys.stdout = pl

    mainwindow.mainloop()

if __name__ == '__main__':
    main()