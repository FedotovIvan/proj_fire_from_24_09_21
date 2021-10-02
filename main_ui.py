import sys
from PyQt5 import QtWidgets, uic
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
import pyqtgraph as pg

from ui_py import Ui_MainWindow as MainForm
from main_lopp import main_loop_class
from xml_parser import xml_parser

class my_ui_class(QtWidgets.QMainWindow,):
    def __init__(self):
        super().__init__()
        self.ui = MainForm()
        self._translate = QtCore.QCoreApplication.translate

        self.ui.setupUi(self)
        self.ui.connect_bt.clicked.connect(self.xss)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_func)

        self.list_table = []

        #test
        self.xml = xml_parser()
        self.mainloop = main_loop_class(self.xml.read_all_xml_data())
        self.mainloop.list_state["work"] = 1
        self.my_data = self.mainloop.get_all_data_to_ui()
        self.create_table_rate()
        self.create_table_data()

        self.timer.start(500)

    def xss(self):
        self.xml = xml_parser()
        self.mainloop = main_loop_class(self.xml.read_all_xml_data())
        self.mainloop.list_state["work"] = 1
        self.my_data = self.mainloop.get_all_data_to_ui()
        self.create_table_rate()
        self.create_table_data()

    def create_table_rate(self):
        num_flow_meters = 0
        for key in self.my_data["flow_meter"]:
            if self.my_data["flow_meter"][key]["enable"] == str(1):
                self.list_table.append(self.my_data["flow_meter"][key]["name"])
                num_flow_meters += 1

        self.ui.table_rate.setColumnCount(5)
        self.ui.table_rate.setRowCount(num_flow_meters)


        item = self.ui.table_rate.horizontalHeaderItem(0)
        item.setText(self._translate("MainWindow", "окно ввода"))
        self.ui.table_rate.horizontalHeader().resizeSection(0, 100)
        #item.setSizeHint(QtCore.QSize(20, 10))

        item = self.ui.table_rate.horizontalHeaderItem(1)
        item.setText(self._translate("MainWindow", "текущий расход"))
        self.ui.table_rate.horizontalHeader().resizeSection(1, 100)
        #item.setSizeHint(QtCore.QSize(20, 10))

        item = self.ui.table_rate.horizontalHeaderItem(2)
        item.setText(self._translate("MainWindow", "задание"))
        self.ui.table_rate.horizontalHeader().resizeSection(2, 100)
        #item.setSizeHint(QtCore.QSize(20, 10))

        item = self.ui.table_rate.horizontalHeaderItem(3)
        item.setText(self._translate("MainWindow", "температура"))
        self.ui.table_rate.horizontalHeader().resizeSection(3, 90)

        item = self.ui.table_rate.horizontalHeaderItem(4)
        item.setText(self._translate("MainWindow", "OK?"))
        self.ui.table_rate.horizontalHeader().resizeSection(4, 50)




    def refresh_table_rate(self):
        x = 0
        for key in self.my_data["flow_meter"]:
            if self.my_data["flow_meter"][key]["enable"] == str(1):
                item = self.ui.table_rate.verticalHeaderItem(x)

                item.setText(self._translate("MainWindow", self.my_data["flow_meter"][key]["name"]))
                rate = self.my_data["flow_meter"][key]["valume"]
                temp = self.my_data["flow_meter"][key]["valume"]
                try:
                    self.ui.table_rate.setItem(x, 1, QtWidgets.QTableWidgetItem(str("%.04f (%.03f)"%(rate[0],rate[2]))))
                    self.ui.table_rate.setItem(x, 3, QtWidgets.QTableWidgetItem(str("%.03f"%temp[1])))
                    self.ui.table_rate.setItem(x, 4, QtWidgets.QTableWidgetItem("?"))
                    if self.my_data["dampers"][key]["ready_task"] == str(1):

                        self.ui.table_rate.item(x, 4).setBackground(QtGui.QColor(0, 255, 0))
                    else:
                        self.ui.table_rate.item(x, 4).setBackground(QtGui.QColor(255, 0, 0))
                    if self.my_data["dampers"][key]["mode"] =="q":
                        self.ui.table_rate.setItem(x, 2, QtWidgets.QTableWidgetItem(str("(q)"+self.my_data["dampers"][key]["q"])))
                    elif self.my_data["dampers"][key]["mode"] =="time":
                        if self.my_data["dampers"][key]["dir"] == 1:
                            self.ui.table_rate.setItem(x, 2, QtWidgets.QTableWidgetItem( "(+)"+str(self.my_data["dampers"][key]["time"]) ))
                        if self.my_data["dampers"][key]["dir"] == 3:
                            self.ui.table_rate.setItem(x, 2, QtWidgets.QTableWidgetItem( "(-)"+str(self.my_data["dampers"][key]["time"]) ))

                except Exception as e:
                    print(e)
                x += 1
        x = 0
        #надо доделать item
    def create_table_data(self):
        item = self.ui.table_data.horizontalHeaderItem(0)
        item.setText(self._translate("MainWindow", "Имя"))
        self.ui.table_data.horizontalHeader().resizeSection(0, 85)
        # item.setSizeHint(QtCore.QSize(20, 10))

        item = self.ui.table_data.horizontalHeaderItem(1)
        item.setText(self._translate("MainWindow", "значение"))
        self.ui.table_data.horizontalHeader().resizeSection(1, 85)
        # item.setSizeHint(QtCore.QSize(20, 10))

        item = self.ui.table_data.horizontalHeaderItem(2)
        item.setText(self._translate("MainWindow", "Имя"))
        self.ui.table_data.horizontalHeader().resizeSection(2, 85)
        # item.setSizeHint(QtCore.QSize(20, 10))

        item = self.ui.table_data.horizontalHeaderItem(3)
        item.setText(self._translate("MainWindow", "Значение"))
        self.ui.table_data.horizontalHeader().resizeSection(3, 85)

    def refresh_table_data(self):
        i = 0
        for key in self.my_data["mb1_device"]:

            self.ui.table_data.setItem(i , 0, QtWidgets.QTableWidgetItem(str(self.my_data["mb1_device"][key]["name"])))
            self.ui.table_data.setItem(i, 1, QtWidgets.QTableWidgetItem(str("%.03f" % self.my_data["mb1_device"][key]["valume"])))
            i += 1
        i = 0
        for key in self.my_data["mb2_device"]:

            self.ui.table_data.setItem(i, 2, QtWidgets.QTableWidgetItem(str(self.my_data["mb2_device"][key]["name"])))
            self.ui.table_data.setItem(i, 3, QtWidgets.QTableWidgetItem(str("%.03f" % self.my_data["mb2_device"][key]["valume"])))
            i += 1
    def timer_func(self):

        self.mainloop._read_all_data()
        self.my_data = self.mainloop.get_all_data_to_ui()
        self.refresh_table_data()
        self.refresh_table_rate()
        print(self.my_data["flow_meter"])

    def press_enter(self):
        '''print(self.ui.table_rate.item(0,0).text())
        str_in = str(self.ui.table_rate.item(0, 0).text())
        if not str_in:
            print("emply")
        #dir = str(self.ui.table_rate.item(0, 0).text())[0]
        self.ui.text_error.setText(str_in)
        '''

        for i in self.list_table:
            thing = self.ui.table_rate.item(self.list_table.index(i), 0)
            if thing is not None and self.ui.table_rate.item(self.list_table.index(i), 0).text() != '':

                str_in = str(self.ui.table_rate.item(self.list_table.index(i), 0).text())
                x = self.check_str(str_in)
                for key in self.my_data["flow_meter"]:
                    if self.my_data["flow_meter"][key]["name"] == i:
                        if x != -1:
                            if str_in[0] == "+":
                                self.mainloop.set_new_task("time", str_in[1:], 0, 1, key)
                            elif str_in[0] == "-":
                                self.mainloop.set_new_task("time", str_in[1:], 0, 3, key)
                            else: self.mainloop.set_new_task("q", 0, str_in, 3, key)





    def check_str(self, string_in):
        if not string_in:
            return -1




    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == QtCore.Qt.Key_Return:
            self.press_enter()
        else:
            super().keyPressEvent(qKeyEvent)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = my_ui_class()
    main.show()
    sys.exit(app.exec_())