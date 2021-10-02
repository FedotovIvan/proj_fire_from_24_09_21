import xml.etree.cElementTree as ET


class xml_parser:
    def __init__(self):
        self.damp_names = ["one","two","three","four","five"]
        self.damp_enable = [1,1,0,1,0]
        self.flow_meter_names = ["one1","two1","three1","four1","five1"]
        self.flow_meter_enable = [1,1,0,1,0]

        self.mb1_names = ["one","two","three","four","five","6","7","8"]
        self.mb1_enable = [1,1,1,1,1,1,1,1]
        self.mb2_names = ["one","two","three","four","five","6","7","8"]
        self.mb2_enable = [1,1,1,1,1,1,1,1]
        self.dam = []
        self.flow = []
        self.mb1 = []
        self.mb2 =[]

    def set_new_parametr(self,damp_names,damp_enable,flow_meter_names,flow_meter_enable,
                         mb1_names, mb1_enable,mb2_names, mb2_enable,flow_meter_id,flow_meter_ch,
                         damp_id,damp_ch,mb1_ch,mb1_id,mb2_ch,mb2_id,error):

        self.root = ET.Element("root")
        self.devices = ET.SubElement(self.root, "devices")
        for i in range(0, 5):
            self.dam.append(ET.SubElement(self.devices, "damper{}".format(i + 1), name=damp_names[i]))
            self.dam[i].set("enable", str(damp_enable[i]))
            self.dam[i].set("num_ch",str(damp_ch[i]))
            self.dam[i].set("id",str(damp_id[i]))
            self.dam[i].set("error", str(error[i]))
        for i in range(0, 5):
            self.flow.append(ET.SubElement(self.devices, "flow_meter{}".format(i + 1), name=flow_meter_names[i]))
            self.flow[i].set("enable", str(flow_meter_enable[i]))
            self.flow[i].set("num_ch",str(flow_meter_ch[i]))
            self.flow[i].set("id", str(flow_meter_id[i]))
        for i in range(0, 8):
            self.mb1.append(ET.SubElement(self.devices, "mb1_ch{}".format(i + 1), name=mb1_names[i]))
            self.mb1[i].set("enable", str(mb1_enable[i]))
            self.mb1[i].set("num_ch",str(mb1_ch[i]))
            self.mb1[i].set("id",str(mb1_id[i]))
        for i in range(0, 8):
            self.mb2.append(ET.SubElement(self.devices, "mb2_ch{}".format(i + 1), name=mb2_names[i]))
            self.mb2[i].set("enable", str(mb2_enable[i]))
            self.mb2[i].set("num_ch", str(mb2_ch[i]))
            self.mb2[i].set("id", str(mb2_id[i]))
        self.tree = ET.ElementTree(self.root)
        self.tree.write("xml_data_init.xml")

    def read_all_xml_data(self):
        damp_names = []
        damp_enable= []
        damp_ch =[]
        flow_meter_enable = []
        flow_meter_names = []
        flow_meter_ch =[]
        mb1_names = []
        mb1_enable = []
        mb1_ch = []

        mb2_names = []
        mb2_enable = []
        mb2_ch = []
        flow_meter_id =[]
        flow_meter_ch =[]

        damp_id=[]
        damp_ch=[]
        mb1_ch=[]
        mb1_id=[]
        mb2_ch=[]
        mb2_id=[]
        error_damp =[]
        one = ET.parse("xml_data_init.xml")
        root1 = one.getroot()
        for i in range (0,5):
            damp_names.append(root1[0][i].get("name"))
            damp_enable.append(root1[0][i].get("enable"))
            damp_ch.append(root1[0][i].get("num_ch"))
            damp_id.append(root1[0][i].get("id"))
            error_damp.append(root1[0][i].get("error"))
        for i in range(5, 10):
            flow_meter_names.append(root1[0][i].get("name"))
            flow_meter_enable.append(root1[0][i].get("enable"))
            flow_meter_ch.append(root1[0][i].get("num_ch"))
            flow_meter_id.append(root1[0][i].get("id"))
        for i in range(10, 18):
            mb1_names.append(root1[0][i].get("name"))
            mb1_enable.append(root1[0][i].get("enable"))
            mb1_ch.append(root1[0][i].get("num_ch"))
            mb1_id.append(root1[0][i].get("id"))
        for i in range(18, 26):
            mb2_names.append(root1[0][i].get("name"))
            mb2_enable.append(root1[0][i].get("enable"))
            mb2_ch.append(root1[0][i].get("num_ch"))
            mb2_id.append(root1[0][i].get("id"))
        lib = {"damp_names":damp_names,"damp_enable":damp_enable,"flow_meter_names":flow_meter_names,"flow_meter_enable":flow_meter_enable,
               "mb1_names":mb1_names,"mb1_enable":mb1_enable,"mb2_names":mb2_names,"mb2_enable":mb2_enable,"mb1_ch":mb1_ch,"mb2_ch":mb2_ch,
               "flow_meter_ch":flow_meter_ch,"damp_ch":damp_ch,"flow_meter_id":flow_meter_id,"damp_id":damp_id,"mb1_id":mb1_id, "mb2_id":mb2_ch,
               "error":error_damp}
        return lib


if __name__ == '__main__':
    x = xml_parser()
    damp_names = ["one","two","three","four","five"]
    damp_enable = [0,0,0,0,0]
    flow_meter_names = ["one1","two1","three1","four1","five1"]
    flow_meter_enable = [1,1,1,0,0]
    mb1_names = ["one","two","three","four","five","6","7","8"]
    mb1_enable = [1,1,1,1,0,0,0,0]
    mb2_names = ["one","two","three","four","five","6","7","8"]
    mb2_enable = [0,0,0,0,0,0,0,0]
    flow_meter_id = [2,3,4,5,0]
    flow_meter_ch = [0,1,2,3,4]
    damp_id = [1,1,1,1,1]
    err = [1, 1, 0, 1, 0]
    damp_ch = [0,1,2,3,4]
    mb1_ch = [0,1,2,3,4,5,6,7]
    mb1_id = [16,16,16,16,16,16,16,16]
    mb2_ch = [0,1,2,3,4,5,6,7]
    mb2_id = [1,1,1,1,1,1,1,1]

    x.set_new_parametr(damp_names,damp_enable,flow_meter_names,flow_meter_enable,mb1_names,mb1_enable,mb2_names,mb2_enable,flow_meter_id,
                       flow_meter_ch,damp_id,damp_ch,mb1_ch,mb1_id,mb2_ch,mb2_id,err)
    print(x.read_all_xml_data())