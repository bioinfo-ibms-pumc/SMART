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
import pickle
from core import SearchModel
import sqlite3



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
    parser.add_argument('-l', '--model', required=True,
                        help="MLR model file for formula assignment.")
    #parser.add_argument('-e', '--extension', action="store_true",
    #                       help="Include extension candidates for formula assignment. ")
    parser.add_argument('-m', '--ppm', default=5, help="PPM threshold for formula assignment (Default: 5).")


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
        out = open(args.input.split("/")[-1] +".smart_results.txt","w")
        out.write("mz\tRawFormula\tID\tFormula\tm/z\tppm\tscore\tDB\n")
        conn = sqlite3.connect(args.database)
        cur = conn.cursor()
        fin = open(args.model,"rb")
        lr = pickle.load(fin)
        fin.close()
        i = 0
        with open(args.input,"r") as infile:
            for line in infile:
                mzs = line.strip().split("\t")
                if mzs[0] == "mz":continue
                mz = mzs[0]
                i += 1
                #res = sm.search(mz,iontag,cur,args.extension,ppm_error=args.ppm,verbose=False)
                res = sm.search(mz,iontag,cur,ppm_error=args.ppm,lr=lr,verbose=False)
                if len(res) > 0:
                    #for s in res:
                    #print(i,mz,s)
                    out.write(line.strip() + "\t" + "\t".join(list(map(str,res[0]))) +"\n")
                else:
                    out.write(line.strip() + "\n")
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
        #res = sm.search(mz,iontag,cur,args.extension,ppm_error=args.ppm,verbose=False)
        res = sm.search(mz,iontag,cur,ppm_error=args.ppm,verbose=False)
        title = ["MZ","id","formula","mz","ppm","score","source"]
        print("{0:3s}{1:^15s}{2:^10s}{3:^15s}{4:^15s}{5:^10s}{6:^10s}{7:^10s}".format("Rank",title[0],title[1],title[2],title[3],title[4],title[5],title[6]))
        rank = 0
        for s in res:
            rank += 1
            if rank > 10:break
            if len(s) > 0:
                print("{0:3d}{1:^15s}{2:^10d}{3:^15s}{4:^15.4f}{5:^10.3f}{6:^10.3f}{7:^10s}".format(rank,mz,s[0],s[1],s[2],s[3],s[4],s[5]))
            else:
                print("{0:3d}{1:^15s}".format(rank,mz))



if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if args.input is not None:
        run_cmd(args)
    else:
        parser.print_help()
    exit()
