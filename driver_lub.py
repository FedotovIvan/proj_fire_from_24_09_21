import minimalmodbus
import time
from random import randint

from collections import deque
import datetime
from random import randint

class flow_meter_class:
    def __init__(self, port=0, slave_id_modbus=0, baundrate=9600, stopbit=1, bytesize=8,
                 timeout=1, register_flow=0, register_temp=0, debug=False, default_valume=4, is_no_air=False):
        self.port = port
        self.slave_id_modbus = slave_id_modbus
        self.baundrate = baundrate
        self.stopbit = stopbit
        self.bytesize = bytesize
        self.timeout = timeout
        self.register_flow = register_flow
        self.register_temp = register_temp

        self.debug = debug
        self.default_valume = default_valume
        self.is_no_air = is_no_air
        self.prev_flow = 0

        if self.debug == False:
            self.instr = minimalmodbus.Instrument(self.port, self.slave_id_modbus, minimalmodbus.MODE_RTU)
            self.instr.serial.baudrate = self.baundrate  # Baud
            self.instr.serial.bytesize = self.bytesize
            self.instr.serial.stopbits = self.stopbit
            self.instr.serial.timeout = self.timeout
            self.instr.mode = minimalmodbus.MODE_RTU
            self.instr.clear_buffers_before_each_transaction = True
        else:
            print("debug init")

        self.flow = 0
        self.temp = 0

    def read_register(self, addr):
        check = 0
        ok = 0
        x = -1
        while check < 4:
            try:
                if self.is_no_air == True:
                    x = self.instr.read_float(addr, 4, 2)
                else:
                    x = self.instr.read_float(addr, 4, 2)
                ok = 1
            except:
                check += 1
                ok = 0
            if ok == 1:
                return x
        return x

    def read_temp_and_flow(self):
        x = 0
        if self.debug == False:
            if self.is_no_air == False:
                self.flow = self.read_register(self.register_flow)
                self.temp = self.read_register(self.register_temp)
            else:
                self.flow = self.read_register(self.register_flow)
                self.temp = 0
            x = self.flow - self.prev_flow
            self.prev_flow = self.flow
        else:
            self.flow = self.default_valume + randint((-1) * self.default_valume, self.default_valume) / 10
            self.temp = self.default_valume + randint((-1) * self.default_valume, self.default_valume) / 10
        return [self.flow, self.temp, x]


class mx110_read_data:
    def __init__(self, port=0, slave_id_modbus=0, baundrate=9600, stopbit=1, bytesize=8,
                 timeout=1, debug=False, default_valume=4):
        self.port = port
        self.slave_id_modbus = slave_id_modbus
        self.baundrate = baundrate
        self.stopbit = stopbit
        self.bytesize = bytesize
        self.timeout = timeout

        self.debug = debug
        self.default_valume = default_valume

        self.data = [0, 0, 0, 0, 0, 0, 0, 0]
        self.register = [4, 10, 16, 22, 28, 34, 40, 46]

        if self.debug == False:
            self.instr = minimalmodbus.Instrument(self.port, self.slave_id_modbus, minimalmodbus.MODE_RTU)
            self.instr.serial.baudrate = self.baundrate  # Baud
            self.instr.serial.bytesize = self.bytesize
            self.instr.serial.stopbits = self.stopbit
            self.instr.serial.timeout = self.timeout
            self.instr.mode = minimalmodbus.MODE_RTU
            self.instr.clear_buffers_before_each_transaction = True
        else:
            print("debug init mb")

    def read_register(self, addr):
        check = 0
        ok = 0
        x = -1
        while check < 3:
            try:
                x = self.instr.read_float(addr, 4, 2)
                ok = 1
            except:
                check += 1
                ok = 0
            if ok == 1:
                return x
        return x

    def read_data(self):  # new function
        if self.debug == False:
            for i in range(0, 7):
                self.data[i] = self.read_register(self.register[i])
        else:
            for i in range(0, 7):
                self.data[i] = self.default_valume + randint((-1) * self.default_valume, self.default_valume) / 10

        return self.data

    def read_one_channel(self, num_chan):
        if self.debug == False:
                x = self.read_register(self.register[num_chan])
        else:
                x = self.default_valume + randint((-1) * self.default_valume, self.default_valume) / 10
        return x



class owen:
    def __init__(self, port=0, slave_id_modbus=0, baundrate=9600, stopbit=1, bytesize=8,
                 timeout=1, debug=False):
        self.port = port
        self.slave_id_modbus = slave_id_modbus
        self.baundrate = baundrate
        self.stopbit = stopbit
        self.bytesize = bytesize
        self.timeout = timeout

        self.debug = debug

        self.ready_q = [0, 0, 0, 0, 0]
        self.close_or = []
        self.open_or = []

        self.time = 3000

        self.register_time = [2, 10, 11]
        self.register_start_q = [0, 4, 5]
        self.register_dir_q = [1, 6, 7]
        self.register_ready_q = [3, 8, 9]

        if self.debug == False:
            self.instr = minimalmodbus.Instrument(self.port, self.slave_id_modbus, minimalmodbus.MODE_RTU)
            self.instr.serial.baudrate = self.baundrate  # Baud
            self.instr.serial.bytesize = self.bytesize
            self.instr.serial.stopbits = self.stopbit
            self.instr.serial.timeout = self.timeout
            self.instr.mode = minimalmodbus.MODE_RTU
            self.instr.clear_buffers_before_each_transaction = True
        else:
            print("debug start")

    def read_register(self, addr_reg):
        check = 0
        while check == 0:
            check = 1
            try:
                data = self.instr.read_register(addr_reg)
            except:
                check = 0
        return data

    def write_register(self, adrr, valume):
        check = 0
        while check == 0:
            check = 1
            try:
                self.instr.write_register(adrr, valume)
            except:
                check = 0

    def open_q(self, num_q, time):
        if self.debug == False:
            self.write_register(self.register_time[num_q ], time)
            self.write_register(self.register_dir_q[num_q ], 1)
            self.write_register(self.register_start_q[num_q ], 1)
            self.ready_q[num_q - 1] = 0
        else:
            self.ready_q[num_q - 1] = 0

    def close_q(self, num_q, time):
        if self.debug == False:
            self.write_register(self.register_time[num_q ], time)
            self.write_register(self.register_dir_q[num_q ], 3)
            self.write_register(self.register_start_q[num_q ], 1)
            self.ready_q[num_q - 1] = 0
        else:
            self.ready_q[num_q - 1] = 0

    def open_all_q(self, num_q):
        if self.debug == False:
            self.write_register(self.register_dir_q[num_q - 1], 2)
            self.write_register(self.register_start_q[num_q - 1], 1)
            self.ready_q[num_q - 1] = 0
        else:
            self.ready_q[num_q - 1] = 0

    def close_all_q(self, num_q):
        if self.debug == False:
            self.write_register(self.register_dir_q[num_q - 1], 4)
            self.write_register(self.register_start_q[num_q - 1], 1)
            self.ready_q[num_q - 1] = 0
        else:
            self.ready_q[num_q - 1] = 0

    def read_ready(self):
        if self.debug == False:
            self.ready_q[0] = self.read_register(self.register_ready_q[0])
            self.ready_q[1] = self.read_register(self.register_ready_q[1])
            self.ready_q[2] = self.read_register(self.register_ready_q[2])
            self.ready_q[3] = 0
            self.ready_q[4] = 0
            # self.ready_q[3] = self.read_register(self.register_ready_q[3])
            # self.ready_q[4] = self.read_register(self.register_ready_q[4])
            return self.ready_q
        else:
            return [1, 1, 1, 1, 1]


