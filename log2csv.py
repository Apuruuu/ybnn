import os
import sys, getopt
import argparse
import datetime
import csv

class Conversion():
    def __init__(self, input_file, output_file, merge_time):
        self.headers = ['time']
        self.rows = []

        log_file = open(input_file)
        time_cache = ''
        self.datas = {}
        for line in log_file:
            time_last, _, data = line.split("  | ")

            print(time_last, type(time_last), data, type(data))

            if len(data)<5 : continue

            if time_cache == '' : time_cache = datetime.datetime.strptime(time_last,"%Y-%m-%d %H:%M:%S")            

            # 计算时间差
            time_last_format = datetime.datetime.strptime(time_last,"%Y-%m-%d %H:%M:%S")
            if (time_last_format - time_cache).seconds > merge_time:
                self.datas = {**self.datas, **{'time':str(time_cache)}}
                self.put_row_into_rows()
                time_cache = time_last_format

            self.datas = {**self.datas, **eval(data)}

        self.datas = {**self.datas, **{'time':str(time_cache)}}
        self.put_row_into_rows()
            
        with open(output_file,'w', newline='')as f:
            f_csv = csv.writer(f)
            f_csv.writerow(self.headers)
            f_csv.writerows(self.rows)

    def put_row_into_rows(self):
        for key in self.datas:
            if key not in self.headers : self.headers.append(key)
        row = [''] * len(self.headers)
        for key in self.headers:
            if key in self.datas.keys(): row[self.headers.index(key)] = self.datas[key]
        self.rows.append(row)
        self.datas = {}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='log2csv')
    parser.add_argument('--log','-l', metavar='L', required=True, type=str, help='The HISTORY path')
    parser.add_argument('--csv','-c', metavar='O', type=str, help='Output CSV file path. defaule is \x1B[3mLOG_FILENAME.TXT\x1B[23m.csv')
    parser.add_argument('--merge','-m', metavar='M', type=int, default=0, help='Data with an interval of t seconds will be considered the same time. Defalut=0 Each row will be recorded separately')
    args = parser.parse_args()

    if args.csv == None : args.csv = args.log + '.csv'

    Conversion(args.log, args.csv, args.merge)