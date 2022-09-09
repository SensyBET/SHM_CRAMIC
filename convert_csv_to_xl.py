from openpyxl import Workbook
import csv

def convert_csv_xls(file):
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

if __name__ == "__main__":
    pass