import time
from datetime import datetime
import minimalmodbus
from driver_lub import owen, mx110_read_data, flow_meter_class
from threading import Thread
import xml_parser

class driver_hard:
    def __init__(self):
        self.task_q = [{"mode": "none", "time": 1000, "dir": 1, "q": 0.54},
                       {"mode": "none", "time": 1000, "dir": 1, "q": 0.54},
                       {"mode": "none", "time": 1000, "dir": 1, "q": 0.54},
                       {"mode": "none", "time": 1000, "dir": 1, "q": 0.54},
                       {"mode": "none", "time": 1000, "dir": 1, "q": 0.54}
                       ]

        self.current_q   = [0, 0, 0, 0, 0]
        self.current_T_q = [0, 0, 0, 0, 0]
        self.current_T_mx = [0, 0, 0, 0, 0, 0, 0, 0]
        self.current_P   = [0, 0, 0, 0, 0, 0, 0, 0]
        self.error       = [0.02, 0.02, 0.01, 0.3, 0.3]
        self.ready_task  = [0, 0, 0, 0, 0]
        self.ready_owen  = [0, 0, 0, 0, 0]
        self.ready_pid   = [0, 0, 0, 0, 0]
        self.task_is_new = [0, 0, 0, 0, 0]

        self.mx_T = mx110_read_data(debug=True)
        self.mx_P = mx110_read_data("COM7",16)
        self.ow = owen("COM7",1)
        self.q1 = flow_meter_class("COM7",2,register_flow=167,register_temp=171)
        self.q2 = flow_meter_class("COM7",3,register_flow=167,register_temp=171)
        self.q3 = flow_meter_class("COM7",4,register_flow=167,register_temp=171)
        self.q4 = flow_meter_class("COM7",5,register_flow=0,register_temp=171,is_no_air= True, debug=False)
        self.q5 = flow_meter_class(debug=True)


    def _read_all_data_dev(self):

        x1 = self.q1.read_temp_and_flow()
        x2 = self.q2.read_temp_and_flow()
        x3 = self.q3.read_temp_and_flow()
        x4 = self.q4.read_temp_and_flow()
        x5 = self.q5.read_temp_and_flow()
        self.current_q = [x1[0], x2[0], x3[0], x4[0], x5[0]]
        self.current_T_q = [x1[1], x2[1], x3[1], x4[1], x5[1]]
        self.current_T_mx = self.mx_T.read_data()
        self.current_P = self.mx_P.read_data()
        self.ready_owen = self.ow.read_ready()



    def loop_hard(self):
        while 1 == 1:
            self._rule_device()
            self._read_all_data_dev()
            self._is_ready_task()
            print("i here")
            #time.sleep(0.5)

    def _rule_device(self):
        for i in range(1,4):
            if self.task_is_new[i-1] == 1:
                if self.task_q[i-1]["mode"] == "time":
                    if self.task_q[i-1]["dir"] == 1:
                        self.ow.open_q(i, self.task_q[i-1]["time"])
                    if self.task_q[i-1]["dir"] == 2:
                        self.ow.open_all_q(i)
                    if self.task_q[i-1]["dir"] == 3:
                        self.ow.close_q(i, self.task_q[0]["time"])
                    if self.task_q[i-1]["dir"] == 4:
                        self.ow.close_all_q(i)
                    self.task_is_new[i - 1] = 0
                    self.ready_task[i - 1] = 0
            if self.task_q[i-1]["mode"] == "q":
                self._my_pid(i,self.task_q[i-1]["q"])
                self.ready_task[i-1] = 0

    def _is_ready_task(self):
        self.ready_owen = self.ow.read_ready()
        for i in range(1,5):
            if self.task_q[i-1]["mode"] == "time":
                if self.ready_owen[i-1] == 1:
                    self.ready_task[i-1] = 1
            if self.task_q[i - 1]["mode"] == "q":
                if self.ready_pid[i-1] == 1:
                    self.ready_task[i-1] = 1



    def _my_pid(self, num_q, task):
        self.ready_owen = self.ow.read_ready()

        if self.ready_owen[num_q-1] == 1:
            self.ready_pid[num_q - 1] = 0
            if self.current_q[num_q-1] > task + self.error[num_q-1]:
                self.ow.close_q(num_q, 500)
            elif self.current_q[num_q-1] < task - self.error[num_q-1]:
                self.ow.open_q(num_q, 500)
            else:
                self.ready_pid[num_q - 1] = 1


    def get_all_data_to_ui(self):
        return [self.current_q, self.current_T_q,
                self.current_P, self.current_T_mx,
                self.task_q, self.ready_task]

    def set_new_task(self, mode ='none' , time = 500, q = 0, dir = 0, num_q = 0):
        if self.task_q[num_q - 1]["mode"] == mode:
            if self.task_q[num_q - 1]["q"] == q:
                if self.task_q[num_q - 1]["dir"] == dir:
                    if self.task_q[num_q - 1]["time"] == time:
                        self.task_is_new[num_q-1] = 0
                        return
        self.task_is_new[num_q-1] = 1

        if mode == 'time':
            self.task_q[num_q-1] = {"mode": "time", "time": time, "dir": dir, "q": q}
        if mode == 'q':
            self.task_q[num_q - 1] = {"mode": "q", "time": time, "dir": dir, "q": q}
    def set_new_err(self,num,err):
        self.error[num-1] = err


class main_loop_class:
    def __init__(self, init_param):
        self.comport = "COM10"
        self.init_debag = False

        self.mb1_device ={}
        self.mb2_device = {}
        self.flow_meter = {}
        self.dampers = {}
        self.obj_owen ={}
        self.message_error = 0
        self.list_state = {"work": 0,
                           "period1": 0,
                           "period2": 0,
                           "save": 0,
                           "start_save": 1,
                           "out_pid": 1}
        self.err_PID_D = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0}
        self.prev_err_PID_D = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0}


        for i in range(0,5):
            self.dampers[init_param["damp_ch"][i]] = {"enable": init_param["damp_enable"][i],
                                                    "error":init_param["error"][i],
                                                    "name":init_param["damp_names"][i],
                                                    "id":init_param["damp_id"][i],
                                                      "is_new_task":0,
                                                      "ready_move":0,
                                                      "mode": "time",
                                                      "time": 0,
                                                      "q":0,
                                                      "dir":0}
        for i in range(0,5):
            self.flow_meter[init_param["flow_meter_ch"][i]] = {"valume": [0,0,0],
                                                                "enable": init_param["flow_meter_enable"][i],
                                                                "name":init_param["flow_meter_names"][i],
                                                               "id":init_param["flow_meter_id"][i]}
        for i in range(0,8):
            self.mb1_device[init_param["mb1_ch"][i]] = {"valume": 0,
                                                        "enable": init_param["mb1_enable"][i],
                                                        "name":init_param["mb1_names"][i],
                                                        "id":init_param["mb1_id"][i]}
        for i in range(0,8):
            self.mb2_device[init_param["mb2_ch"][i]] = {"valume": 0,
                                                        "enable": init_param["mb2_enable"][i],
                                                        "name":init_param["mb2_names"][i],
                                                        "id": init_param["mb2_id"][i]}
        print(self.flow_meter)
        print(self.mb1_device)
        print(self.mb2_device)
        print(self.dampers)
        for key in self.flow_meter:
            if self.flow_meter[key]["enable"] == str(1):
                if int(key) < 3:
                    self.flow_meter[key]["obj"] = flow_meter_class(self.comport,int(self.flow_meter[key]["id"]),
                                                                   register_flow=167,register_temp=171,debug=self.init_debag)
                else:
                    self.flow_meter[key]["obj"] = flow_meter_class(self.comport, int(self.flow_meter[key]["id"]),
                                                                   register_flow=0, register_temp=171,
                                                                   debug=self.init_debag, is_no_air=True)


        print(self.flow_meter)
        for key in self.mb1_device:
            if self.mb1_device[key]["enable"] == str(1):
                self.mb1_device[key]["obj"] = mx110_read_data(self.comport,int(self.mb1_device[key]["id"]),debug=self.init_debag)
        for key in self.mb2_device:
            if self.mb2_device[key]["enable"] == str(1):
                self.mb2_device[key]["obj"] = mx110_read_data(self.comport, int(self.mb2_device[key]["id"]),debug=self.init_debag)
        print(self.mb1_device)
        for key in self.dampers:
            if self.dampers[key]["enable"] == str(1):
                self.obj_owen = owen(self.comport,int(self.dampers[key]["id"]),debug=self.init_debag)
                break

    def _read_all_data(self):
        try:
            for key in self.flow_meter:
                if self.flow_meter[key]["enable"] == str(1):
                    self.flow_meter[key]["valume"] = self.flow_meter[key]["obj"].read_temp_and_flow()
            for key in self.mb1_device:
                if self.mb1_device[key]["enable"] == str(1):
                    self.mb1_device[key]["valume"] = self.mb1_device[key]["obj"].read_one_channel(int(key))
            for key in self.mb2_device:
                if self.mb2_device[key]["enable"] == str(1):
                    self.mb2_device[key]["valume"] = self.mb2_device[key]["obj"].read_one_channel(int(key))
            '''ready_or  = self.obj_owen.read_ready()
            for key in self.dampers:
                self.dampers[key]["ready_move"] = ready_or[int(key)]'''
        except Exception as e:
            print(e)
            self.message_error = "что-то не так с опросом"

    def set_new_task(self, mode='none', time=500, q=0, dir=0, key = 0):
            self.dampers[str(key)]["mode"] = mode
            self.dampers[str(key)]["time"] = time
            self.dampers[str(key)]["q"] = q
            self.dampers[str(key)]["dir"] = dir
            self.dampers[str(key)]["ready_task"] = 0
            self.dampers[str(key)]["is_new_task"] = 1

    def _rule_device(self):
        for key in self.dampers:
            if self.dampers[key]["is_new_task"] == 1 and self.dampers[key]["enable"] == str(1):
                if self.dampers[key]["mode"] == "time":
                    if self.dampers[key]["dir"] == 1:
                        self.obj_owen.open_q(int(key),int(self.dampers[key]["time"]))
                    if self.dampers[key]["dir"] == 2:
                        self.obj_owen.open_all_q(int(key))
                    if self.dampers[key]["dir"] == 3:
                        self.obj_owen.close_q(int(key),int(self.dampers[key]["time"]))
                    if self.dampers[key]["dir"] == 4:
                        self.obj_owen.close_all_q(int(key))
                    self.dampers[key]["ready_task"] = 0
                    self.dampers[key]["ready_move"] = 0
                    self.dampers[key]["is_new_task"] = 0
                if self.dampers[key]["mode"] == "q":
                    self.dampers[key]["ready_task"] = 0
                    self._my_pid(key,self.dampers[key]["q"])
    def _my_pid(self,key,q):
        if self.flow_meter[key]["valume"][0] != -1:
            if self.dampers[key]["ready_move"] == 1:
                self.dampers[key]["ready_task"] = 0
                out = self.calculate_pid(float(self.flow_meter[key]["valume"][0]), float(self.dampers[key]["q"]),key)
                if float(self.dampers[key]["q"]) < float(q) + float(self.dampers[key]["error"]):
                    if out > 4000:
                        print("close",key,"=", 4000)
                        self.obj_owen.open_q(int(key), 4000)
                    if out >90 and out<4000:
                        print("close", key, "=", out)
                        self.obj_owen.open_q(int(key), int(out))
                    self.dampers[key]["ready_move"] = 0

                if float(self.dampers[key]["q"]) > float(q) - float(self.dampers[key]["error"]):

                    if int(out) < -4000:
                        print("open", key, "=", 4000)
                        self.obj_owen.close_q(int(key), 4000)
                    if int(out) < -90 and int(out) > -4000:
                        print("open", key, "=", out)
                        self.obj_owen.close_q(int(key),(-1)*int(out))
                    self.dampers[key]["ready_move"] = 0

                if float(self.dampers[key]["q"]) < float(q) - float(self.dampers[key]["error"]) and float(self.dampers[key]["q"]) > float(q) + float(self.dampers[key]["error"]):
                    self.dampers[key]["ready_task"] = 1
                self.dampers[key]["ready_move"] = 0
            self.dampers[key]["ready_move"] = 0

    def calculate_pid(self, current_valume, task, key):
        kp = 10500
        kd = 100
        self.err_PID_D[key] = task - current_valume
        d = (self.err_PID_D[key] - self.prev_err_PID_D[key])
        self.prev_err_PID_D[key] = self.err_PID_D[key]
        out = (self.err_PID_D[key] * kp + d * kd)
        self.list_state["out_pid"] = out
        return out




    def _is_ready_task(self):
        for key in self.dampers:
            if self.dampers[key]["mode"] == "time" and  self.dampers[key]["ready_move"] == 1:
                self.dampers[key]["ready_task"] = 1

    def read_test_data(self):
        for key in self.flow_meter:
            if self.flow_meter[key]["enable"] == str(1):
                self.flow_meter[key]["valume"] = self.flow_meter[key]["obj"].read_temp_and_flow()
        for key in self.mb1_device:
            if self.mb1_device[key]["enable"] == str(1):
                self.mb1_device[key]["valume"] = self.mb1_device[key]["obj"].read_one_channel(int(key))
        for key in self.mb2_device:
            if self.mb2_device[key]["enable"] == str(1):
                self.mb2_device[key]["valume"] = self.mb2_device[key]["obj"].read_one_channel(int(key))
        return [self.flow_meter, self.mb1_device]

    def get_all_data_to_ui(self):
        return {"dampers":self.dampers, "flow_meter":self.flow_meter,"mb1_device":self.mb1_device,"mb2_device":self.mb2_device}

    def main_loop(self):
        while self.list_state["work"] == 1:
            try:
                start_time = time.time()
                self._read_all_data()
                self.save_data()
                ready_or = self.obj_owen.read_ready()
                self._is_ready_task()
                for key in self.dampers:
                    self.dampers[key]["ready_move"] = ready_or[int(key)]
                self._rule_device()
                self.list_state["period1"] = time.time() - start_time
            except:
                print("что-то не так в главном цикле")

    def main_loop_owen(self):
        while self.list_state["work"] == 1:
            start_time = time.time()

            ready_or = self.obj_owen.read_ready()
            self._is_ready_task()
            for key in self.dampers:
                self.dampers[key]["ready_move"] = ready_or[int(key)]
            self._rule_device()
            self.list_state["period2"] = time.time() - start_time


    def save_data(self):
        if self.list_state["save"] == 0:
            try:
                self.file.close()
            except:
                print("файл закрыт")
            return
        if self.list_state["start_save"] == 1:
            timestr = time.strftime("%Y_%m_%d-%H_%M_%S")
            self.file = open("data_" + timestr + '.txt', "w")
            str_head = ""
            for key in self.flow_meter:
                if self.flow_meter[key]["enable"] == str(1):
                    str_head += str(self.flow_meter[key]["name"])
                    str_head += "flow,"
                    str_head += str(self.flow_meter[key]["name"])
                    str_head += "temp,"
            for key in self.mb1_device:
                if self.mb1_device[key]["enable"] == str(1):
                    str_head += str(self.mb1_device[key]["name"])
                    str_head += ","
            for key in self.mb2_device:
                if self.mb2_device[key]["enable"] == str(1):
                    str_head += str(self.mb2_device[key]["name"])
                    str_head += ","
            '''for key in self.dampers:
                if self.dampers[key]["enable"] == str(1):
                    str_head += "заслонка_"
                    str_head += str(key)
                    str_head += "_задача,"'''
            str_head +="\n"
            self.file.write(str_head)
            self.list_state["start_save"] = 0
        str_data = ""
        for key in self.flow_meter:
            if self.flow_meter[key]["enable"] == str(1):
                str_data += str(self.flow_meter[key]["valume"][0])
                str_data += ","
                str_data += str(self.flow_meter[key]["valume"][1])
                str_data += ","
        for key in self.mb1_device:
            if self.mb1_device[key]["enable"] == str(1):
                str_data += str(self.mb1_device[key]["valume"])
                str_data += ","
        for key in self.mb2_device:
            if self.mb2_device[key]["enable"] == str(1):
                str_data += str(self.mb2_device[key]["valume"])
                str_data += ","
        str_data += datetime.now().strftime("%Y.%m.%d.%H.%M.%S.%f")
        #str_data += time.strftime("%Y,%m,%d,%H,%M,%S,%f")
        str_data += "\n"
        self.file.write(str_data)






if __name__ == '__main__':
    '''
    ow = owen("COM11",1)
    ow.open_q(1, 2000  )
    #time.sleep(5)
    ow.close_q(1,2000)
    '''
    y  = xml_parser.xml_parser()
    x = main_loop_class(y.read_all_xml_data())
    x.list_state["work"] = 1
    while 1 ==1:
        time.sleep(0.5)
        x.main_loop()
        print(x.get_all_data_to_ui())
