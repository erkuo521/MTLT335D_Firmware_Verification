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
import sys
import can
import time
import struct
import threading
import subprocess
from communicator import aceinna_can
from communicator import aceinna_uart


from queue import Queue # only python3 supported now

class aceinna_driver(): 
    def __init__(self, debug_mode = False):   
        self.can = aceinna_can()
        self.msg_queue_lock = threading.Lock()
        self.msg_queue = Queue()
        self.can_nodes = []
        self.devs = {} # 'src':'aceinna_device'   
        self.debug = debug_mode  
   
        self.thread_put     = threading.Thread(target=self.clollect_msg)
        self.thread_provide = threading.Thread(target=self.provide_msg)
        self.start_record()

        self.uart = aceinna_uart()     # init port and baudrate when use    

    def get_can_nodes(self):
        '''
        it will select nodes from all nodes list, request: 128 to 255
        '''
        # empty msg queue
        self.msg_queue_lock.acquire()    
        if self.msg_queue.empty():
            self.msg_queue_lock.release()            
        else:
            self.msg_queue.queue.clear()
            self.msg_queue_lock.release()
        self.send_wakeup_msg()
        
        time.sleep(2)
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':self.can_nodes})
        return [x for x in self.can_nodes if x in range(0x80, 0x100)] # range check[128, 256) 

    def start_record(self):
        '''
        start 2 threads to collect msgs and provider to right dev
        '''
        self.send_wakeup_msg() 
        self.thread_put.start()
        self.thread_provide.start()

    def send_wakeup_msg(self): 
        '''
        for MTLT will enable auto baud function, which keep silent at first. need send msg to wake up it
        '''
        for i in range(5):
            time.sleep(0.1)
            self.send_can_msg(0x18EAFF06, [00000000])

    def send_can_msg(self, id, data):
        if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[hex(id)] + [hex(x) for x in data]})
        return self.can.send_msg(id_int=id, data_list=data)

    def clollect_msg(self):
        while True:
            msg_raw = self.can.get_msg()
            msg_pdu = self.get_pdu_list(msg=msg_raw)            
            if msg_pdu['src'] not in self.can_nodes: # detect src for all nodes
                self.can_nodes.append(msg_pdu['src'])
                self.can_nodes.sort() # from small to big, sorted

            # if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':msg_pdu})
            self.msg_queue_lock.acquire()
            self.msg_queue.put(msg_pdu)
            self.msg_queue_lock.release()

    def provide_msg(self):
        while True:
            self.msg_queue_lock.acquire()    
            if self.msg_queue.empty(): #is empty or not
                self.msg_queue_lock.release()
                time.sleep(0.001)
                continue 
            else:
                msg = self.msg_queue.get()
                self.msg_queue_lock.release()
                if msg['src'] in self.devs:
                    # if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[msg['src'], self.devs]})
                    instance_dev = self.devs[msg['src']]
                    # if self.debug: eval('print([k, i])', {'k':sys._getframe().f_code.co_name, 'i':instance_dev != None})               
                    if instance_dev != None:
                        instance_dev.get_pdu_msg(msg)
                    else:
                        pass  # to be added

    def register_dev(self, dev_src, instance_dev):
        '''
        all devs registered in driver
        '''
        if dev_src in self.devs:
            return False
        else:
            self.devs[dev_src] = instance_dev
            return True

    def get_pdu_list(self, msg = None, msg_dict = None):
        pdu_dict = {}
        msg_list = list(str(msg).split(" "))     # the list include: time, id, priority, DLC, data0,data1,...,data7
        msg_list = [x for x in msg_list if x != '']       # delete the empty items      
        pdu_dict["time_stamp"] = float(msg_list[0])
        pdu_dict["id"] = int(msg_list[1],16)
        pdu_dict["extended_id"] = msg.id_type
        pdu_dict["priority"] = int(msg_list[2],2)
        pdu_dict["src"] = 0x000000FF & int(msg_list[1],16)
        pdu_dict["dlc"] = int(msg_list[3],10)
        pdu_dict["pgn"] = (0x00FFFF00 & int(msg_list[1],16)) >> 8
        pdu_dict["payload"] = ''.join(msg_list[4:])        
        return pdu_dict    

    def send_get_uart_msg(self, data):
        get_value = []
        if self.uart.UUT == None:
            self.uart.set_uut("/dev/ttyUSB0", 57600)
        for i in range(5):
            self.uart.send_msg(data)
            get_value = self.uart.get_msg()
            if len(get_value) != 0:
                break
            time.sleep(0.5)    
        if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':get_value})

        return get_value