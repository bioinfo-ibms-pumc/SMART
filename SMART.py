#########################################################################
# File Name: SMART.py
# > Author: CaoYinghao
# > Mail: caoyinghao@gmail.com
# Created Time: Thu May 16 10:05:37 2024
#########################################################################
#! /usr/bin/python

import glob
import sys
import re
import os
import argparse
from core import SearchModel
import sqlite3


#self.sm.search(mz,iontag,self.cur,self.extendtag.isChecked(),ppm_error=ppm,verbose=False)

def get_parser():
    desc = """Program: SMART_CMD
Version: 1.0
 Email : <yhcao@ibms.pumc.edu.cn>
      """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)

    parser.add_argument('-i', '--input', required=True,
                           help="Input file/mz_value for formula assignment (Only table format supported).")
    # runparser.add_argument('-o', '--output', required = True, help="Output prefix for metabolite extraction.")
    parser.add_argument('-p', '--polarity', default="+",
                        help="Polarity information for formula assignment. (Default: +, [-,0])")
    parser.add_argument('-d', '--database', required=True,
                        help="SMART-Database file for formula assignment.")
    parser.add_argument('-e', '--extension', default=False,
                           help="Include extension candidates for formula assignment. ")
    parser.add_argument('-m', '--ppm', default=5, help="PPM threshold for formula assignment (Default: 5).")
    parser.add_argument('-v', '--verbose', default=False,
                        help="Peak group per mz for formula assignment (Default: 5; Only integer large than 1).")

    return parser

def check_float(s):
    if s.count('.') == 1:  # 判断小数点个数
        sl = s.split('.')  # 按照小数点进行分割
        left = sl[0]  # 小数点前面的
        right = sl[1]  # 小数点后面的
        if left.startswith('-') and left.count('-') == 1 and right.isdigit():
            lleft = left.split('-')[1]  # 按照-分割，然后取负号后面的数字
            if lleft.isdigit():
                return False
        elif left.isdigit() and right.isdigit():
            # 判断是否为正小数
            return True
    elif s.isdigit():
        s = int(s)
        if s != 0:
            return True

def run_cmd(args):
    sm = SearchModel()
    if os.path.exists(args.input):
        iontag = -1
        if args.polarity == "-":
            iontag = 1
        elif args.polarity == "+":
            iontag = 0
        out = open(args.input +".smart_results.txt","w")
        out.write("ID\tRank\tFormula\tm/z\tppm\tscore\tDB\n")
        conn = sqlite3.connect(args.database)
        cur = conn.cursor()
        with open(args.input,"r") as infile:
            for line in infile:
                mz = line.strip()
                res = sm.search(mz,iontag,cur,args.extension,ppm_error=args.ppm,verbose=False)
                for s in res:
                    print(mz,s)
                    out.write("\t".join(list(map(str,s))) +"\n")
        out.close()
        print("Results is saved to " + args.input + ".smart_results.txt")
                
    else:
        mz = args.input
        if not check_float(str(args.ppm)):
            print("Error, PPM needs integer/float value.")
            exit()
        if not check_float(mz):
            print("Error, "+ mz+ " needs integer/float value.")
            exit()
        if not os.path.exists(args.database):
            print("Error, "+ database+ " is not exists")
            exit()
        conn = sqlite3.connect(args.database)
        cur = conn.cursor()
        mz = args.input
        iontag = -1
        if args.polarity == "-":
            iontag = 1
        elif args.polarity == "+":
            iontag = 0
        res = sm.search(mz,iontag,cur,args.extension,ppm_error=args.ppm,verbose=False)
        for s in res:
            print(mz,s)



if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if args.input is not None:
        run_cmd(args)
    else:
        parser.print_help()
    exit()
