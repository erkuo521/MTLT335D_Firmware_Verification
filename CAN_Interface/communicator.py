'''
mtlt products(MTLT305D and 300RI included now) CAN Bus read and send message module
Requires PI3B and CAN_HAT(shopping link: https://m.tb.cn/h.eRtgNe2)
with H/L of CAN_HAT connected with H/L from sensor side
follow http://www.waveshare.net/wiki/RS485_CAN_HAT 
or follow blog at http://skpang.co.uk/blog/archives/1220
only store the angle, acc, rate to can_data.txt
running in hardbyte-python-can foler, downloaded from https://bitbucket.org/hardbyte/python-can/get/4085cffd2519.zip
@author: cek
'''

import os
import time
import can
import subprocess
import serial

#j1939 with extended id
class aceinna_can(): 
    def __init__(self, chn = 'can0', bus_type = 'socketcan_ctypes'):   
        if os.sys.platform.startswith('lin'):    
            os.system('sudo /sbin/ip link set can0 up type can bitrate 250000')  # run this command first with correct baud rate
        else:
            print('not linux system, pls running on linux system')
        self.can0 = can.interface.Bus(channel = chn, bustype = bus_type)  # socketcan_native

    def send_msg(self, id_int, data_list):  # id_int = 0x18FF5500, data_list =[128, 1, 0, 0, 0, 0, 0, 0] set ODR is 100hz
        send_msg = can.Message(arbitration_id=id_int, data=data_list, extended_id=True)
        cmd = 'sudo /sbin/ip -details link show can0'
        res = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        feedback = res.stdout.read().decode('utf-8')
        # print(feedback)
        if 'BUS-OFF' not in feedback:
            self.can0.send(send_msg)
            return True
        else:
            print('bus-off now')
            cmd = 'sudo /sbin/ip link set can0 type can restart-ms 100'
            res = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            return False
    
    def get_msg(self):
        return self.can0.recv()

class aceinna_uart(): 
    def __init__(self):   
        self.baudrate = None
        self.port = None
        self.UUT = None
        self.header_bytes = 2
        self.packet_type_bytes = 2
        self.payload_len_bytes = 1
        self.crc_bytes = 2

    def send_msg(self, data):  # data is list
        self.UUT.write(data)
    
    def set_uut(self, port, baudrate):
        self.baudrate = baudrate
        self.port = port
        self.UUT = serial.Serial(port, baudrate, timeout = 2)
        self.send_msg(data=[0x55, 0x55, 0x57, 0x46, 0x05, 0x01, 0x00, 0x01, 0x00, 0x00, 0x4f, 0xec]) # request to keep quiet
    
    def get_msg(self, timeout = 10):
        retry = 0
        t0 = time.time()
        str_list = []
        while True:
            hex = self.UUT.read(1).hex()
            if(len(hex) == 0):
                if(time.time() - t0 > timeout):
                    #print "timed out"
                    return str_list

            elif(hex == '55'):
                hex = self.UUT.read(1).hex()
                if(hex == '55'):
                    #once header found, read other fields from the packet
                    str_list.append(self.UUT.read(self.packet_type_bytes).hex())
                    #print "Packet Type = " + packet_type
                    payload_size = self.UUT.read(self.payload_len_bytes).hex()
                    str_list.append(payload_size)
                    str_list.append(self.UUT.read(int(payload_size,16)).hex())
                    #print "Data = " + data_hex
                    str_list.append(self.UUT.read(self.crc_bytes).hex())
                    #print "CRC = " + crc_hex
                    return str_list
            else:    # gets here if it received a byte that is not header(0x55)
                retry += 1
                t0 = time.time()
                if(retry > 100):
                    print("Error: Couldnt find header")
                    return str_list


    