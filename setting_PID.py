import sys
import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QGridLayout,QLabel, QLineEdit, QApplication,QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtCore
from driver_lub import flow_meter_class,owen


class MyThread(QThread):
    signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__()
        self.s = None
        self.phase = 0
        self.comport = "COM7"

        self.flow_meter = flow_meter_class(self.comport,2,register_flow=167,register_temp=171,debug=True)
        self.owen = owen(self.comport,1,debug=True)
        self.MAXSIZE = 70
        self.arr = np.empty(self.MAXSIZE, dtype=np.float32)
        for i in range(0, self.MAXSIZE):
            self.arr[i] = 0
        self.q =[0,0,0]
        self.kp = 10000
        self.ki = 0
        self.kd = 50
        self.dt = 1
        self.set_point = 0
        self.integral = 0
        self.prev_err =0
        self.out = 0



    def run(self):
        while 1  == 1:
            #for i in range(50000):
            self.update()
            self.signal.emit([self.arr, self.out])
            self.msleep(100)

    def update(self):
        self.q = self.flow_meter.read_temp_and_flow()
        self.add_data(self.q[0])
        if self.owen.read_ready()[0] == 1:
            self.out = self.my_pid()
            print(self.out)
            print(self.q)
            if (self.out > 50 or self.out < -50) and (self.out < 5000 or self.out > -5000):
                if self.out > 0:
                    self.owen.open_q(0,self.out)
                else:
                    self.owen.close_q(0, (-1)*self.out)

    def my_pid(self):
        self.err = self.set_point - self.q[0]
        self.integral += self.err * self.dt
        self.D = (self.err - self.prev_err)/self.dt
        self.prev_err = self.err
        return (self.err * self.kp + self.integral * self.ki + self.D * self.kd)

    def add_data(self,data):
        for i in  range(0,self.MAXSIZE):
            if i == self.MAXSIZE-1:
                self.arr[i] = data
                return
            self.arr[i] = self.arr[i+1]
    def set_new_pid(self,kp, ki,kd,dt):
        self.kp = kp
        self.ki = ki
        self.kd = kd



class Window(QDialog):
    def __init__(self):
        super().__init__()

        self.gridLayoutCreation()

        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.groupBox)
        self.setLayout(vboxLayout)

        self.traces = dict()
        pg.setConfigOptions(antialias=True)

    def gridLayoutCreation(self):
        self.groupBox = QGroupBox("Пример компоновки Grid Layout")
        gridLayout = QGridLayout()
        self.guiplot = pg.PlotWidget()
        gridLayout.addWidget(self.guiplot, 0, 8, 8, 12)
        self.groupBox.setLayout(gridLayout)



        self.stop_bt = QPushButton(self.groupBox)
        self.stop_bt.setGeometry(QtCore.QRect(20, 150, 75, 23))
        self.stop_bt.setText("save")
        self.stop_bt.clicked.connect(self.save_set)

        self.kp = QLineEdit(self.groupBox)
        self.kp.setGeometry(QtCore.QRect(10, 180, 50, 20))
        self.kp.setObjectName("kp")

        self.kp1 = QLabel(self.groupBox)
        self.kp1.setGeometry(QtCore.QRect(80, 180, 50, 20))
        self.kp1.setObjectName("kp1")
        self.kp1.setText("P")

        self.kp2 = QLabel(self.groupBox)
        self.kp2.setGeometry(QtCore.QRect(90, 180, 50, 20))
        self.kp2.setObjectName("kp2")
        self.kp2.setText("P")

        self.ki = QLineEdit(self.groupBox)
        self.ki.setGeometry(QtCore.QRect(10, 210, 50, 20))
        self.ki.setObjectName("ki")

        self.ki1 = QLabel(self.groupBox)
        self.ki1.setGeometry(QtCore.QRect(80, 210, 50, 20))
        self.ki1.setObjectName("ki1")
        self.ki1.setText("i")

        self.ki2 = QLabel(self.groupBox)
        self.ki2.setGeometry(QtCore.QRect(90, 210, 50, 20))
        self.ki2.setObjectName("ki2")
        self.ki2.setText("i")

        self.kd = QLineEdit(self.groupBox)
        self.kd.setGeometry(QtCore.QRect(10, 240, 50, 20))
        self.kd.setObjectName("kd")

        self.kd1 = QLabel(self.groupBox)
        self.kd1.setGeometry(QtCore.QRect(80, 240, 50, 20))
        self.kd1.setObjectName("kd1")
        self.kd1.setText("d")
        self.kd2 = QLabel(self.groupBox)
        self.kd2.setGeometry(QtCore.QRect(90, 240, 50, 20))
        self.kd2.setObjectName("kd2")
        self.kd2.setText("d")

        self.timeEdit = QLineEdit('Hello World')
        gridLayout.addWidget(self.timeEdit, 1, 0)

        self.kq = QLineEdit(self.groupBox)
        self.kq.setGeometry(QtCore.QRect(10, 50, 50, 20))
        self.kq.setObjectName("kq")

        self.stop_bt1 = QPushButton(self.groupBox)
        self.stop_bt1.setGeometry(QtCore.QRect(10, 20, 75, 23))
        self.stop_bt1.setText("save_q")
        self.stop_bt1.clicked.connect(self.save_q)

        self.kq1 = QLabel(self.groupBox)
        self.kq1.setGeometry(QtCore.QRect(80, 50, 50, 20))
        self.kq1.setObjectName("kq1")
        self.kq1.setText("q")

        self.kq2 = QLabel(self.groupBox)
        self.kq2.setGeometry(QtCore.QRect(100, 50, 50, 20))
        self.kq2.setObjectName("kq2")
        self.kq2.setText("q")

    def save_q(self):
        if self.kq.text() != "":
            x = self.kq.text()
        else:
            x = 0
        cc = float(x)
        print(cc)
        self.thread.set_point = cc

    def save_set(self):

        if self.kp.text() != "":
            x = self.kp.text()
        else:
            x = 0
        if self.ki.text() != "":
            y = self.ki.text()
        else:
            y = 0
        if self.kd.text() != "":
            z = self.kd.text()
        else:
            z = 0

        self.thread.set_new_pid(float(x),float(y),float(z),1)


    def plotar(self, s):
        self.guiplot.clear()
        self.guiplot.plot(s)

    def test(self):
        self.thread = MyThread()
        self.thread.signal.connect(self.displayS)
        self.thread.start()

    def displayS(self, self_s):
        """ Рисуйте график в реальном времени, не блокируя графический интерфейс.
        """
        self.timeEdit.setText(str("%.00f"%self_s[1]))
        self.kp2.setText(str(self.thread.kp))
        self.ki2.setText(str(self.thread.ki))
        self.kd2.setText(str(self.thread.kd))
        self.kq2.setText(str(self.thread.set_point))
        self.plotar(self_s[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    w.test()
    sys.exit(app.exec_())