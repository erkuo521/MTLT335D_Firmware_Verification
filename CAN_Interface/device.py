'''
version 1.1.0 in Aceinna
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
import json

from queue import Queue #only python3 supported now
from driver import aceinna_driver


class aceinna_device(): 
    def __init__(self, source_address, attribute_json, debug_mode = False, power_gpio = None):
        # self.power_pin = pwr_pin # positve of power pin 
        self.auto_power = power_gpio
        self.src = source_address
        self.sn_can  = None
        self.default_confi = {}
        self.req_ext_id_templete = 0x18EAFF00
        self.predefine = attribute_json['predefine']
        self.can_attribute = attribute_json['configuration']['can']
        self.sw_rst_support = False if (self.get_item_json(namestr = 'save_config')['restart_support'] != 'TRUE') else True
        self.type_name = attribute_json['type']
        self.driver = None
        self.debug = debug_mode

        self.auto_msg_queue = []
        self.auto_msg_queue_lock = []
        self.req_feedback_payload = []
        self.set_feedback_payload = []

        self.init_data_list()
        self.init_default_confi() 

    def add_driver(self, driver_instance):
        self.driver = driver_instance

    def update_sn(self):
        '''
        calc sn number, which include last 5 fugures in hex format sn(on housing surface). 
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        ecu_id_payload = self.request_cmd(cmd_name = 'ecu_id')
        # if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':ecu_id_payload})
        high_16bits_value = int(ecu_id_payload[-2:] + ecu_id_payload[-4:-2], 16) << 5
        low_5bits_value = int(ecu_id_payload[-6:-4], 16) >> 3
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':ecu_id_payload})
        self.sn_can = high_16bits_value + low_5bits_value  # it is the last 5 figures in whole hex_sn.
    
    def init_default_confi(self):
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        self.default_confi['pkt_rate'] = self.predefine.get('pkt_rate') if 'pkt_rate' in self.predefine else 1 # pkt_rate index default config, if it is 1--100hz, if it's 5---20hz
        self.default_confi['pkt_type'] = self.predefine.get('pkt_type') if 'pkt_type' in self.predefine else 7
        self.default_confi['lpf_filter'] = self.predefine.get('lpf_filter') if 'lpf_filter' in self.predefine else [25, 5] # lpf_rate, lpf_acc lpf_filter
        self.default_confi['orientation'] = self.predefine.get('orientation') if "orientation" in self.predefine else [0, 0] # import orientation default config
        self.default_confi['unit_behavior'] = self.predefine.get('unit_behavior') if 'unit_behavior' in self.predefine else 146
        self.default_confi['unit_behavior_rawrate'] = self.predefine.get('unit_behavior_rawrate') if 'unit_behavior_rawrate' in self.predefine else 0
        self.default_confi['algo_ctl'] = self.predefine.get('algo_ctl') if 'algo_ctl' in self.predefine else "00D007D0070A00"
        self.default_confi['bank_ps0'] = [int(x, 16) for x in list(self.predefine['set_bank_ps0']['ps_default'].values())]
        self.default_confi['bank_ps1'] = [int(x, 16) for x in list(self.predefine['set_bank_ps1']['ps_default'].values())]

    def init_data_list(self):
        '''
        based on JSON file, create several queues and locks for auto-send data
        create list for request cmd feedback and set cmd feedbacks, correspond to idx in each json item
        '''
        auto_list = [x for x in self.can_attribute if x['type'] == 'auto']
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':auto_list})
        request_list = [x for x in self.can_attribute if (x['type'] == 'request')]
        feedback_list = [x for x in self.can_attribute if (x['type'] == 'feedback')]
        for i in range(len(auto_list)):
            self.auto_msg_queue.append(Queue())
            self.auto_msg_queue_lock.append(threading.Lock())
        for j in range(len(request_list)):
            self.req_feedback_payload.append(None)
        for k in range(len(feedback_list)):
            self.set_feedback_payload.append(None)
    
    def empty_data_pkt(self):
        '''
        empty all queues and all request and set feedback lists
        '''
        for idx,item in enumerate(self.auto_msg_queue):
            self.auto_msg_queue_lock[idx].acquire()            
            item.queue.clear()
            self.auto_msg_queue_lock[idx].release() 
        for j in self.req_feedback_payload:
            j = None
        for k in self.set_feedback_payload:
            k = None
        time.sleep(0.2)

    def get_pdu_msg(self, msg_input): # CAN msg
        '''
        called by driver, receive the msg which SA is self.src
        '''
        if msg_input['src'] == self.src:    
            self.put_msg(msg_input.copy())

    def get_item_json(self, namestr = None, pgnnum = None, extsetid = None): 
        '''
        return json item dict which you selected by name/pgnnum/extsetid
        '''       
        if namestr != None:
            return [x for x in self.can_attribute if x['name'] == namestr][0]
        if pgnnum != None:
            pgn_list = [x for x in self.can_attribute if 'pgn' in x]
            pgn_des = [x for x in pgn_list if x['pgn'] == pgnnum]
            if len(pgn_des) == 0:
                return [x for x in pgn_list if x['pgn'] == 'None'][0]  
            else:
                return pgn_des[0]
        if extsetid != None:
            pgn_list = [x for x in self.can_attribute if 'ext_set_id' in x]
            return [x for x in pgn_list if x['ext_set_id'] == extsetid][0]

    def put_msg(self, pdu_msg):
        '''
        put received msg into correspond queue or list, based on pgn and right json item dict
        '''
        pgn_des = self.get_item_json(pgnnum = pdu_msg['pgn'])
        id_name = [x for x in ['auto_id', 'req_id', 'fb_id'] if x in pgn_des][0]
        id_idx = pgn_des[id_name]
        # if pdu_msg['pgn'] == 0xFF59 and self.debug: # debug whether one msg get or not
        #     if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[pgn_des, id_name, id_idx, pdu_msg]})
        if id_name == 'auto_id':  
            self.auto_msg_queue_lock[id_idx].acquire()
            self.auto_msg_queue[id_idx].put(pdu_msg)
            self.auto_msg_queue_lock[id_idx].release()
        elif id_name == 'req_id':
            self.req_feedback_payload[id_idx] = pdu_msg
        elif 'fb_id' in pgn_des:
            self.set_feedback_payload[id_idx] = pdu_msg  
            # if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':self.set_feedback_payload[id_idx]})
        else:
            pass

    def request_cmd(self, cmd_name, unit_behavior_rawrate=False):
        '''
        send cmd and get feedback, based on cmd_type. refer to json
        cmd_names are ['fw_version', 'ecu_id', 'hw_bit', 'sw_bit', 'status', 'pkt_rate', 'pkt_type', 
        'lpf_filter', 'orientation', 'unit_behavior', 'algo_ctl']
        unit_behavior_rawrate is True will receive 3 bytes in feedback, for FW update version.19.1.81 or above
        '''
        pgn_des = self.get_item_json(namestr = cmd_name)
        if len(pgn_des):
            cmd_idx = pgn_des['req_id']
            cmd_pgn = pgn_des['pgn']
            if self.debug: eval('print(k, i, j)', {'k':sys._getframe().f_code.co_name,'i':[cmd_idx] + [cmd_name], 'j':self.req_feedback_payload[cmd_idx]}) 
            self.req_feedback_payload[cmd_idx] = None # set the value which correspond to cmd_idx in list(req_feedback_payload) to None
            if self.debug: eval('print(k, i, j)', {'k':sys._getframe().f_code.co_name,'i':[cmd_idx] + [cmd_name], 'j':self.req_feedback_payload[cmd_idx]}) 
            data = [00, (cmd_pgn >> 8) & 0xFF, cmd_pgn & 0x00FF]  
            for i in range(3): # send 3 times to avoid not working in some abnormal condition
                self.driver.send_can_msg(self.req_ext_id_templete | cmd_idx, data)  
                time.sleep(2)          
                if self.debug: eval('print(k, i, j)', {'k':sys._getframe().f_code.co_name,'i':[hex(x) for x in data] + [cmd_idx] + [cmd_name], 'j':self.req_feedback_payload[cmd_idx]})            
                if self.req_feedback_payload[cmd_idx] != None:
                    temp_payload = self.req_feedback_payload[cmd_idx]['payload']
                    if self.type_name == 'MTLT305D' and cmd_name == 'unit_behavior' and unit_behavior_rawrate == False: # for 305D only return first 2 bytes
                        return temp_payload[0:4]
                    return temp_payload
                else:
                    pass # to be added                 
            return False 
        else:
            return False  

    def new_request_cmd(self, src, new_pgn):
        '''
        if new ps changed and check whether new ps-PGN feedback or not after send new_pgn request
        return new ps-pgn msg payload
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[src, hex(new_pgn)]})
        self.empty_data_pkt()
        time.sleep(2)
        data = [00, (new_pgn >> 8) & 0xFF, new_pgn & 0x00FF]   # first byte is 00 to apply for FW update
        for i in range(3):   
            self.driver.send_can_msg(self.req_ext_id_templete, data) # data: [80 FF 52]
            time.sleep(0.4)
            while True:
                rlt = self.get_payload_auto('unknow')
                if rlt == False:
                    break
                if rlt['pgn'] == new_pgn:
                    return rlt['payload']
        return False

    def set_cmd(self, cmd_name, payload_without_src):
        '''
        cmd_name: ['save_config', 'algo_rst', 'set_pkt_rate','set_pkt_type', 'set_lpf_filter', 'set_orientation', 
        'set_unit_behavior', 'set_algo_ctl', 'set_bank_ps0', 'set_bank_ps1']
        cmd_name should be in reference list;  refer to json
        payload_without_src must be a ***list***. like [00] for [00, 80(added by program automatically)];
        for save_config, payload of byte-0: Request or Response or Reset(save and power cycel); 
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[cmd_name, payload_without_src]})

        pgn_des = [x for x in self.can_attribute if x['type'] == 'set' and x['name'] == cmd_name][0]
        ext_id = pgn_des['ext_set_id']
        if len(pgn_des):    
            if ext_id in [419385600, 419385344]: # this is for ID 0x18FF5100 and 0x18FF5000            
                if (self.sw_rst_support == False) and (payload_without_src == [2]):
                    payload = [0] + [self.src] # save configurations 
                    self.driver.send_can_msg(ext_id, payload)
                    if self.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                        self.auto_power.power_off()
                        time.sleep(4)
                        self.auto_power.power_on()
                    else:
                        while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                            pass
                    time.sleep(1) 
                    self.driver.send_wakeup_msg()
                else:
                    payload = payload_without_src + [self.src] 
                    self.driver.send_can_msg(ext_id, payload)
                    time.sleep(0.1)  
                    self.driver.send_can_msg(ext_id, payload) 
                if payload_without_src == [2]: 
                    time.sleep(0.5)
                    self.driver.send_wakeup_msg()  
                    time.sleep(0.3) 
            elif ext_id in [419426304, 419426560]: # this is for ID 0x18FFF000 and 0x18FFF100
                if self.type_name == 'MTLT305D':
                    payload = payload_without_src
                elif self.type_name == 'MTLT335':
                    payload = [self.src] + payload_without_src
                self.driver.send_can_msg(ext_id, payload) 
                time.sleep(0.1)  
                self.driver.send_can_msg(ext_id, payload)     
            else:
                if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':'HERE246'})
                payload = [self.src] + payload_without_src
                self.driver.send_can_msg(ext_id, payload) 
                time.sleep(0.2)  
                self.driver.send_can_msg(ext_id, payload)  
            return True
        else:
            pass # to be added

    def new_set_cmd(self, new_ps, data):
        '''
        after ps changed by ps cmd, check whether new ps-PGN feedback or not after send new_ps set cmd
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        templeate_id = 0x18FF5000
        new_ext_id = (templeate_id & 0xFFFF00FF) + (new_ps << 8)
        new_pgn = (new_ext_id >> 8) & 0x00FFFF
        self.empty_data_pkt()        
        for i in range(5):
            self.driver.send_can_msg(new_ext_id, data) # 0x18FF6000, [00 80]
            time.sleep(0.2)        
            rlt = self.get_payload_auto('unknow')
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[new_pgn, rlt]})
            if rlt == False:
                break
            if rlt['pgn'] == new_pgn:
                if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':rlt['payload']})
                return rlt['payload']
        return False

    def get_payload_auto(self, auto_name):
        '''
        auto_name:'ssi2', 'rate', 'accel', 'addr', 'ssi', 'acc_hr', 'unknow', refer to json
        unknow packets are used for new PGNs(acc_hr/rate_hr/new request feedback msg/new set cmd feedback msg
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        pgn_des = self.get_item_json(namestr = auto_name)
        id_idx = pgn_des['auto_id']
        try: 
            for i in range(5):
                if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':['before for', pgn_des, id_idx, len(self.auto_msg_queue), len(self.auto_msg_queue_lock)]})
                self.auto_msg_queue_lock[id_idx].acquire()    
                if self.auto_msg_queue[id_idx].empty():
                    self.auto_msg_queue_lock[id_idx].release()      
                    time.sleep(0.001)      
                else:
                    if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':[pgn_des, id_idx, len(self.auto_msg_queue), len(self.auto_msg_queue_lock)]})
                    msg = self.auto_msg_queue[id_idx].get()
                    self.auto_msg_queue_lock[id_idx].release()
                    if auto_name == 'unknow':
                        return msg
                    return msg['payload']   
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':'for end'})      
        except Exception as e:
            print(e, i, len(self.auto_msg_queue), len(self.auto_msg_queue_lock))     
        return False

    def set_get_feedback_payload(self, set_fb_name):
        '''
        auto_name:'save_config_feedback', 'algo_rst_feedback'
        set cmd firstly, and then get the feedback. 
        it include set_cmd too.
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        # pgn_des = [x for x in self.can_attribute if x['type'] == 'feedback' and x['name'] == set_fb_name][0]
        pgn_des = self.get_item_json(namestr = set_fb_name)
        id_idx = pgn_des['fb_id']   
        
        self.set_feedback_payload[id_idx] = None  
        for i in range(3): 
            self.set_cmd(cmd_name = set_fb_name.replace('_feedback',''), payload_without_src = [0]) 
            time.sleep(3)
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[id_idx, self.set_feedback_payload[id_idx]]})        
            if self.set_feedback_payload[id_idx] != None:
                return self.set_feedback_payload[id_idx]['payload']    
            else:
                pass
        return False

    def measure_pkt_type(self, type_num = 5):
        '''
        based on types_data and types_name in json, to calc actual msg 
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        payload = self.request_cmd('pkt_rate')
        while payload == False:
            if self.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.auto_power.power_off()
                time.sleep(4)
                self.auto_power.power_on()
            else:
                while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                    pass
            self.driver.send_wakeup_msg()
            payload = self.request_cmd('pkt_rate')            
        odr_idx = int(payload[-2:], 16)
        time.sleep(0.2)
        self.set_cmd('set_pkt_rate', [1])
        time.sleep(0.2)
        # type_num = len(self.predefine.get("types_name")) # update pkt type numbers based on json, input type_num when use this function.
        exist_list = [0] * type_num 
        self.empty_data_pkt()   
        idx_list = [self.get_item_json(x)['auto_id'] for x in self.predefine.get('types_name')]
        if self.debug: eval('print(k,j,slope)', {'k':sys._getframe().f_code.co_name, 'j': self.auto_msg_queue[idx_list[0]].qsize(), 'slope':'slope_exist:'})        
        time.sleep(2) # wait 1s to receive packets again

        for i in range(type_num): # give right value to each type value in type list
            exist_list[i]  = pow(2, i) if (self.auto_msg_queue[idx_list[i]].qsize() > 0) else 0

        sumexist = sum(exist_list)
        if self.debug: eval('print(k,j,slope,m )', {'k':sys._getframe().f_code.co_name, 'j': self.auto_msg_queue[idx_list[0]].qsize(), 'slope':'slope_exist:','m':exist_list})
        if sumexist == 0 & self.debug:
            if self.debug: input('sumexist of pkt_type is 0, pls press enter:')
        self.set_cmd('set_pkt_rate', [odr_idx])
        time.sleep(0.2)
        return sumexist

    def measure_pkt_rate(self): 
        ''' 
        measure ODR, open the recording and set right packet type 
        measure 5s, calc the average of received accel msg numbers
        ''' 
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        self.set_cmd('set_pkt_type', [7])
        time.sleep(0.2)
        pgn_des = self.get_item_json(namestr = 'accel')
        id_idx = pgn_des['auto_id']    
        self.auto_msg_queue_lock[id_idx].acquire()     
        self.auto_msg_queue[id_idx].queue.clear() 
        self.auto_msg_queue_lock[id_idx].release() 
        time.sleep(5)
        odr = self.auto_msg_queue[id_idx].qsize()/5 
        if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':odr})
        return odr    

    def decode_pke_type_num(self, pkt_num):
        '''
        check each bit value of pkt_num
        '''
        slope_exist       = True if ((pkt_num >> (1-1)) & 1) == 1 else False
        rate_exist        = True if ((pkt_num >> (2-1)) & 1) == 1 else False
        acc_exist         = True if ((pkt_num >> (3-1)) & 1) == 1 else False
        angle_ssi_exist   = True if ((pkt_num >> (4-1)) & 1) == 1 else False
        acc_hr_exist      = True if ((pkt_num >> (5-1)) & 1) == 1 else False
        return slope_exist, rate_exist, acc_exist, angle_ssi_exist, acc_hr_exist

    def decode_behavior_num(self, behavior_num):
        bitsnum = self.predefine['bits_unit_bhr']
        # get each bit value, idx 0 is LSB
        list2 = [((behavior_num >> (x)) & 1) for x in range(bitsnum)]
        if self.debug: eval('print(k, i, j)', {'k':sys._getframe().f_code.co_name,'i':list2, 'j':['behavior_num:', behavior_num]})
        return list2

    def send_get_uart_msg(self, request_data):
        '''
        such as, request_data= [0x55, 0x55, 0x52, 0x46, 0x03, 0x01, 0x00, 0x32, 0xac, 0xfa]
        request CAN address which saved in EEPROM
        '''
        strlist = self.driver.send_get_uart_msg(request_data)
        return strlist
        

    def calc_ssi2(self,msg):   
        '''
        unit: degree
        '''
        pitch_uint = msg.data[0] + 256 * msg.data[1] +  65536 * msg.data[2]
        roll_uint = msg.data[3] + 256 * msg.data[4] +  65536 * msg.data[5]
        pitch = pitch_uint * (1/32768) - 250.0
        roll = roll_uint * (1/32768) - 250.0

        return 'Time: {2:18.6f} Roll: {0:6.2f} Pitch: {1:6.2f}'.format(roll,pitch,msg.timestamp)
        
    def calc_accel(self,msg):   
        '''
        unit: g
        '''    
        ax_ay_az = struct.unpack('<HHHH', msg.data)
        ax = ax_ay_az[0] * (0.01) - 320.0
        ay = ax_ay_az[1] * (0.01) - 320.0
        az = ax_ay_az[2] * (0.01) - 320.0        

        return 'Time: {3:18.6f} AX  : {0:6.2f} AY   : {1:6.2f} AZ: {2:6.2f}'.format(ax,ay,az,msg.timestamp)

    def calc_rate(self,msg):     
        '''
        unit: deg/s
        '''   
        wx_wy_wz = struct.unpack('<HHHH', msg.data)
        wx = wx_wy_wz[0] * (1/128.0) - 250.0
        wy = wx_wy_wz[1] * (1/128.0) - 250.0
        wz = wx_wy_wz[2] * (1/128.0) - 250.0  
        return 'Time: {3:18.6f} WX  : {0:6.2f} WY   : {1:6.2f} WZ: {2:6.2f}'.format(wx,wy,wz,msg.timestamp)
    
    # def ctl_power(self, power_on = False):
    #     if power_on:
    #         GPIO.output(self.power_pin,GPIO.HIGH) 
    #         print('power on now')
    #     else:
    #         GPIO.output(self.power_pin,GPIO.LOW) 
    #         print('power off now')

    def set_to_default(self, pwr_rst = True): # back to default confi and power cycle 
        '''
        set ps cmd to recover all ps cmd, then check unit_behavior cmd to confirm 
        unit is working well, and then set default configurations
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':['pwr_reset_request:',pwr_rst]})
        # set bank ps cmd firstly, let all cmds back default configurations same as User Manual, or some cmd maybe not working              
        for i in ['bank_ps0', 'bank_ps1']:
            self.set_cmd('set_' + i, self.default_confi[i])
        # check whether can get unit behavior or not, to confirm the right feedbac from unit. then can start to set.
        payload = self.request_cmd('unit_behavior', unit_behavior_rawrate=True)
        for i in range(3):   # some times unit will no feedback for 80FF59 Request, need to restart by SW or manualy restart in below
            if payload == False: 
                self.set_cmd('save_config', [2]) # save and power reset
                time.sleep(0.4)
                payload = self.request_cmd('unit_behavior', unit_behavior_rawrate=True)
        while payload == False:
            if self.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.auto_power.power_off()
                time.sleep(4)
                self.auto_power.power_on()
            else:
                while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                    pass
            time.sleep(1)   
            payload = self.request_cmd('unit_behavior', unit_behavior_rawrate=True)
        # set unit behavior to 0, and then configure it to default value based on JSON. alos configure all other items
        # fb_lth_bytes = self.get_item_json('unit_behavior')['fb_length']
        disablebit = int(payload[2:4], 16)
        disablebit_rawrate = int(payload[4:6], 16)
        time.sleep(1)
        if self.type_name == 'MTLT305D':
            self.set_cmd('set_unit_behavior', [0, 0, disablebit, disablebit_rawrate, self.src])
        if self.type_name == 'MTLT335RI': #335RI not fulfill disable bit function
            self.set_cmd('set_unit_behavior', [0, disablebit, 0, self.src])
        time.sleep(1)
        for i in ['algo_ctl', 'pkt_rate','pkt_type', 'lpf_filter', 'orientation', 'bank_ps0', 'bank_ps1']:
            if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i': i})
            if isinstance(self.default_confi[i], list):
                self.set_cmd('set_' + i, self.default_confi[i])
            elif i == 'algo_ctl' and isinstance(self.default_confi['algo_ctl'], str):
                self.set_cmd('set_' + i, [int(self.default_confi['algo_ctl'][x:x+2], 16) for x in range(0,13,2)])
            else:
                self.set_cmd('set_' + i, [self.default_confi[i]])
        time.sleep(1)
        # set unit behavior based on different unit type
        if self.type_name == 'MTLT305D':
            self.set_cmd('set_unit_behavior', [self.default_confi['unit_behavior'], self.default_confi['unit_behavior_rawrate'], 0, 0, self.src])
        elif self.type_name == 'MTLT335':
            # self.set_cmd('set_unit_behavior', [self.default_confi['unit_behavior']])
            self.set_cmd('set_unit_behavior', [self.default_confi['unit_behavior'], self.default_confi['unit_behavior_rawrate'], 0, 0, self.src])

        time.sleep(1)
        if pwr_rst: # check whether support sw-reboot or not
            if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':'will power reset'})
            self.set_cmd('save_config', [2]) # save and power reset
            time.sleep(1)
        self.driver.send_wakeup_msg()
        return True  

'''
        # pgn_list = [x for x in self.can_attribute if x['name'] == 'None']
        # pgn_des = [x for x in pgn_list if x['pgn'] == 'None'][0]
        # id_name = [x for x in ['auto_id', 'req_id', 'fb_id'] if x in pgn_des][0]
        # id_idx = pgn_des[id_name] 
        # return pgn_des, id_name, id_idx

        # pgn_list = [x for x in self.can_attribute if 'pgn' in x]
        # pgn_des_list = [x for x in pgn_list if x['pgn'] == pdu_msg['pgn']]
        # pgn_des = pgn_des_list[0] if len(pgn_des_list) else [x for x in pgn_list if x['pgn'] == 'None'][0]  


        #     print(self.auto_msg_queue[id_idx].qsize())

        # pgn_des = [x for x in self.can_attribute if x['type'] == 'request' and x['name'] == cmd_name][0]

        # pgn_des = [x for x in self.can_attribute if x['type'] == 'auto' and x['name'] == auto_name][0]

        # slope_exist       = 1 if (self.auto_msg_queue[idx_list[0]].qsize() > 0) else 0
        # rate_exist        = 2 if self.auto_msg_queue[idx_list[1]].qsize() > 0 else 0
        # acc_exist         = 4 if self.auto_msg_queue[idx_list[2]].qsize() > 0 else 0
        # angle_ssi_exist   = 8 if self.auto_msg_queue[idx_list[3]].qsize() > 0 else 0
        # hr_acc_exist      = 16 if self.auto_msg_queue[idx_list[4]].qsize() > 0 else 0  
        # list1 = [slope_exist, rate_exist, acc_exist, angle_ssi_exist, hr_acc_exist]
        # slope_exist, rate_exist, acc_exist, angle_ssi_exist, hr_acc_exist = 0, 0, 0, 0, 0

        # pgn_des = [x for x in self.can_attribute if x['type'] == 'auto' and x['name'] == 'ssi2'][0]

        # over_range       = ((behavior_num >> (1-1)) & 1)
        # dyna_motion      = ((behavior_num >> (2-1)) & 1)
        # uncorr_rate      = ((behavior_num >> (3-1)) & 1)
        # swap_rateXY      = ((behavior_num >> (4-1)) & 1)
        # autobaud_dete    = ((behavior_num >> (5-1)) & 1)
        # can_term_resistor= ((behavior_num >> (6-1)) & 1)
        # list2 = [over_range, dyna_motion, uncorr_rate, swap_rateXY, autobaud_dete, can_term_resistor]

        # def gpio_setting(self):
    #         GPIO.setmode(GPIO.BCM)
    #         GPIO.setup(self.power_pin,GPIO.OUT)
    #         GPIO.output(self.power_pin,GPIO.HIGH) # used as power positive line  in Pi3 board             
    # def test(self):
    #     while True:
    #         input('pwr off:')
    #         print(self.power.power_pin)
    #         self.power.power_off()
    #         input('pwr on')
    #         self.power.power_on()    

'''



   

    



    



      

