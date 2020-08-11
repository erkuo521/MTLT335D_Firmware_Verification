import os
# import xlwings as xw
import csv

class my_csv():
    def __init__(self, filename_str, openmode = 'w+'):
        try:
            self.outputFile = open(filename_str, openmode, newline='') 
            self.outputWriter = csv.writer(self.outputFile)
        except Exception as e:
            print("pls close csv file.")

    def write(self, datalist, print_too = False):
        if isinstance(datalist[0], list):
            self.outputWriter.writerows(datalist)
        else:
            self.outputWriter.writerow(datalist)
        self.outputFile.flush()
        if print_too:
            print(datalist)

    def __del__(self):
        self.outputFile.close()