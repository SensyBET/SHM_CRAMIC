from sqlite3 import DateFromTicks
import pandas as pd
import glob
import os
from openpyxl import Workbook
import csv
import matplotlib.pyplot as plt
  

def convert_csv_xls(file):
    """Convert given csv file to a xls !!! Beware of the size"""
    wb = Workbook()
    ws = wb.active
    try:
        with open(file, 'r') as f:
            for row in csv.reader(f):
                ws.append(row)
        wb.save(f'{file[:-3]}xlsx')
        print(f'{file[:-3]}xlsx saved')
    except:
        print(f'{file} error')

def __add_to_df(files):
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    print(df)
    return df

def __plot_me(df, x, y):
    # plt.scatter(df[x], df[y])
    df.plot.line(x, y)
    plt.show()
    

def mass_convert_to_xls(folder, fType = "csv"):
    files = []
    for path in os.listdir(folder):
        if path[-4:] == '.csv':
            files.append(f"{folder}/{path}")
    #files = glob.glob(files)
    df = __add_to_df(files)
    try:
        os.mkdir(f"{folder}/merge")
    except:
        pass
    if fType == "xlsx":
        print("The forces of chaos are at work")
        df.to_excel(f"{folder}/merge/MERGE.xlsx")
    elif fType == "csv":
        print("The forces of chaos are at work")
        df.to_csv(f"{folder}/merge/MERGE.csv")
    print(f"Folder dump into {folder}/MERGE.{fType}")
    __plot_me(df,"time (ms)", "CH07 (SNS3_Force1) p=6 DS=1")


if __name__ == '__main__':
    pass