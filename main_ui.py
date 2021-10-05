import sys
from PyQt5 import QtWidgets, uic
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from threading import Thread
from ui_py import Ui_MainWindow as MainForm
from main_lopp import main_loop_class
from xml_parser import xml_parser

class my_ui_class(QtWidgets.QMainWindow,):
    def __init__(self):
        super().__init__()
        self.ui = MainForm()
        self._translate = QtCore.QCoreApplication.translate

        self.ui.setupUi(self)
        self.ui.connect_bt.clicked.connect(self.func_start)
        self.ui.p2_bt_save.clicked.connect(self.save_init_setting)
        self.ui.unconnect.clicked.connect(self.func_unconnect)
        self.ui.save_from_now.clicked.connect(self.func_save_from_now)
        self.ui.save.clicked.connect(self.stop_save)
        self.ui.stop_bt.clicked.connect(self.func_stop_bt)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_func)

        self.list_table = []

        #test
        self.xml = xml_parser()
        self.mainloop = main_loop_class(self.xml.read_all_xml_data())
        self.my_data = self.mainloop.get_all_data_to_ui()
        self.create_table_rate()
        self.create_table_data()

        self.timer.start(200)

    def func_stop_bt(self):
        self.mainloop.set_new_task("time",10,1,4,str(0))
        self.mainloop.set_new_task("time",10,1,4,str(1))
        self.mainloop.set_new_task("time", 10, 1, 4, str(2))
    def stop_save(self):
        self.mainloop.list_state["save"] = 0
    def func_save_from_now(self):
        self.mainloop.list_state["save"] = 1
        self.mainloop.list_state["start_save"] = 1
    def func_unconnect(self):
        self.mainloop.list_state["work"] = 0

    def func_start(self):
        self.xml = xml_parser()
        self.mainloop = main_loop_class(self.xml.read_all_xml_data())
        self.mainloop.list_state["work"] = 1
        self.my_data = self.mainloop.get_all_data_to_ui()
        self.create_table_rate()
        self.create_table_data()
        self.tr = Thread(target=self.mainloop.main_loop)
        self.tr.start()
        self.tr1 = Thread(target=self.mainloop.main_loop_owen)
        self.tr1.start()

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
        self.ui.table_rate.horizontalHeader().resizeSection(0, 70)
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
                    if self.my_data["dampers"][key]["ready_task"] == 1:

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
                    print('ошибка обновления табицы потока')
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

        self.my_data = self.mainloop.get_all_data_to_ui()
        self.refresh_table_data()
        self.refresh_table_rate()
        self.ui.label_20.setText("подключен ли = %d\nпериод датч = %.01f\nпериод овен = %.02f\nсохраняет = %.01f"%(self.mainloop.list_state["work"],
                                                                                                  self.mainloop.list_state["period1"],self.mainloop.list_state["period2"],
                                                                                            self.mainloop.list_state["save"]))

        if self.mainloop.list_state["work"] == 1:
            self.ui.connect_bt.setEnabled(False)
            self.ui.unconnect.setEnabled(True)
        else:
            self.ui.connect_bt.setEnabled(True)
            self.ui.unconnect.setEnabled(False)
        if self.mainloop.list_state["save"] == 0:
            self.ui.save_from_now.setEnabled(True)
            self.ui.save.setEnabled(False)
        else:
            self.ui.save_from_now.setEnabled(False)
            self.ui.save.setEnabled(True)
        #print(self.my_data["flow_meter"])

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
                self.ui.table_rate.item(self.list_table.index(i), 0).setText("")






    def check_str(self, string_in):
        if not string_in:
            return -1

    def save_init_setting(self):
        damp_en = [0,0,0,0,0]
        if self.ui.p2_damp0.isChecked():
            damp_en[0] = 1
        if self.ui.p2_damp1.isChecked():
            damp_en[1] = 1
        if self.ui.p2_damp2.isChecked():
            damp_en[2] = 1
        if self.ui.p2_damp3.isChecked():
            damp_en[3] = 1
        if self.ui.p2_damp4.isChecked():
            damp_en[4] = 1
        flow_enable = [0,0,0,0,0]
        if self.ui.p2_flow0.isChecked():
            flow_enable[0]=1
        if self.ui.p2_flow1.isChecked():
            flow_enable[1]=1
        if self.ui.p2_flow2.isChecked():
            flow_enable[2]=1
        if self.ui.p2_flow3.isChecked():
            flow_enable[3]=1
        if self.ui.p2_flow4.isChecked():
            flow_enable[4]=1
        mb1_en = [0,0,0,0,0,0,0,0]
        if self.ui.p2_en_mb1_ch0.isChecked():
            mb1_en[0]=1
        if self.ui.p2_en_mb1_ch1.isChecked():
            mb1_en[1]=1
        if self.ui.p2_en_mb1_ch2.isChecked():
            mb1_en[2]=1
        if self.ui.p2_en_mb1_ch3.isChecked():
            mb1_en[3]=1
        if self.ui.p2_en_mb1_ch4.isChecked():
            mb1_en[4]=1
        if self.ui.p2_en_mb1_ch5.isChecked():
            mb1_en[5]=1
        if self.ui.p2_en_mb1_ch6.isChecked():
            mb1_en[6]=1
        if self.ui.p2_en_mb1_ch7.isChecked():
            mb1_en[7]=1
        mb2_en = [0, 0, 0, 0, 0, 0, 0, 0]
        mb1_name =["0", '1', '2', '3', "4", "5", "6", "7"]
        mb1_name[0] = self.ui.p2_en_mb1_name0.text()
        mb1_name[1] = self.ui.p2_en_mb1_name1.text()
        mb1_name[2] = self.ui.p2_en_mb1_name2.text()
        mb1_name[3] = self.ui.p2_en_mb1_name3.text()
        mb1_name[4] = self.ui.p2_en_mb1_name4.text()
        mb1_name[5] = self.ui.p2_en_mb1_name5.text()
        mb1_name[6] = self.ui.p2_en_mb1_name6.text()
        mb1_name[7] = self.ui.p2_en_mb1_name7.text()
        mb2_name = ["0", '1', '2', '3', "4", "5", "6", "7"]
        damp_names = ["one", "two", "three", "four", "five"]
        flow_meter_names = ["one1", "two1", "three1", "four1", "five1"]
        flow_meter_id = [2, 3, 4, 5, 0]
        flow_meter_ch = [0, 1, 2, 3, 4]
        damp_id = [1, 1, 1, 1, 1]
        err = [1, 1, 0, 1, 0]
        damp_ch = [0, 1, 2, 3, 4]
        mb1_ch = [0, 1, 2, 3, 4, 5, 6, 7]
        mb1_id = [16, 16, 16, 16, 16, 16, 16, 16]
        mb2_ch = [0, 1, 2, 3, 4, 5, 6, 7]
        mb2_id = [1, 1, 1, 1, 1, 1, 1, 1]
        self.xml.set_new_parametr(damp_names,damp_en,flow_meter_names,flow_enable,mb1_name,mb1_en,mb2_name,mb2_en,flow_meter_id,flow_meter_ch,damp_id,damp_ch,
                                  mb1_ch,mb1_id,mb2_ch,mb2_id,err)

    def load_init_p2_setting(self):
        dat = self.xml.read_all_xml_data()
        if dat["damp_enable"][0] == str(1):
            self.ui.p2_damp0.setChecked(True)
        else:
            pass



    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == QtCore.Qt.Key_Return:
            self.press_enter()
        else:
            super().keyPressEvent(qKeyEvent)

    def closeEvent(self, event):
        self.func_unconnect()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = my_ui_class()
    main.show()
    sys.exit(app.exec_())