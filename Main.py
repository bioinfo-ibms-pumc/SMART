#########################################################################
# File Name: Main.py
# > Author: CaoYinghao
# > Mail: caoyinghao@gmail.com
# Created Time: Thu May 16 10:05:37 2024
#########################################################################
#! /usr/bin/python

import sys
import os

from PyQt5.QtWidgets import QMainWindow,QApplication,QDesktopWidget
from window import Ui_MainWindow
from PyQt5.QtWidgets import QTableWidgetItem,QMessageBox
from PyQt5.QtCore import Qt
from core import SearchModel
import sqlite3
import pickle

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        if not os.path.exists("smart.db"):
            print("Warning, no smart database found.")
        self.conn = sqlite3.connect("smart.db")
        self.cur = self.conn.cursor()
        self.setupUi(self)
        self.predBtn.clicked.connect(self.pred)
        self.sm = SearchModel()

        titles = ['Input', "Rank", 'Formula', 'm/z','ppm', 'score', 'DB']
        for i in range(len(titles)):
            item = QTableWidgetItem()
            item.setText(titles[i])
            self.myTable.setHorizontalHeaderItem(i, item)
        self.myTable.setRowCount(1)

    def check_float(self,s):
        if s.count('.') == 1:  # judge decimal point
            sl = s.split('.')  
            left = sl[0]  
            right = sl[1]  
            if left.startswith('-') and left.count('-') == 1 and right.isdigit():
                lleft = left.split('-')[1]  # negative
                if lleft.isdigit():
                    return False
            elif left.isdigit() and right.isdigit():
                
                return True
        elif s.isdigit():
            s = int(s)
            if s != 0:
                return True
    def pred(self):
        text = self.input.toPlainText()
        print("text",text)
        if text.strip() == "":
            QMessageBox.warning(None, "Error", "No m/z found. Please enter m/z value line by line! ")
            return
        ppm = self.ppm.text()
        if not self.check_float(ppm):
            QMessageBox.warning(None, "Error", "PPM need integer/float value.")
            return

        allmz = []
        allres = []
        iontag = self.group.checkedId()
        rowC = 0
        fin = open("lr_4f.pkl","rb")
        lr = pickle.load(fin)
        fin.close()

        for mz in text.strip().split("\n"):
            if mz == "":continue
            if not self.check_float(mz):
                QMessageBox.warning(None, "Error", mz + " need integer/float value.")
                return
            allmz.append(mz)
            res = self.sm.search(mz,iontag,self.cur,ppm_error=ppm,lr=lr,verbose=False)
            rowC += len(res)
            allres.append(res)
        self.myTable.clear()
        self.myTable.setRowCount(rowC)
        titles = ['Input', "Rank", 'Formula', 'm/z','ppm', 'score', 'DB']
        for i in range(len(titles)):
            item = QTableWidgetItem()
            item.setText(titles[i])
            self.myTable.setHorizontalHeaderItem(i, item)
        c = 0
        for i in range(len(allres)):
            res = allres[i]

            for j in range(len(res)):
                if j > 3:break
                # print(res[j],c)
                item = QTableWidgetItem()
                item.setText(str(allmz[i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.myTable.setItem(c, 0, item)
                if len(res[j]) == 0:
                    for k in range(len(titles)-1):
                        item = QTableWidgetItem()
                        item.setText("-")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.myTable.setItem(c, k + 1, item)
                else:
                    for k in range(len(res[j])):
                        txt = str(res[j][k])
                        if k == 0:
                            txt = str(j)
                        item = QTableWidgetItem()
                        item.setText(txt)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.myTable.setItem(c,k+1,item)
                c += 1

        pass

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        newLeft = int((screen.width() - size.width()) / 2)
        newTop = int((screen.height() - size.height()) / 2)
        self.move(newLeft, newTop)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.center()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

