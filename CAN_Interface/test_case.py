'''
CAN testing script
v1.0.0 20200509 erkuo chen
'''

import os
import sys
import time
import struct
import datetime
from device import aceinna_device # need to be delete

class aceinna_test_case():
    def __init__(self, testfile, debug_mode = False):
        self.dev = None
        self.debug = debug_mode
        self.fw_num = None
        self.test_file = testfile # csv write and read        
        self.test_case = []
        self.init_test_dict()
        self.function_measure_data = {}

    def set_test_dev(self, dev_instance, fwnum):        
        self.dev = dev_instance
        self.fw_num = fwnum
        
    def run_test_case(self, test_item = [], start_idx = 0): 
        '''
        main function: to run the test functions which listed in test_case list
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[len(self.test_case), test_item]})
        self.dev.empty_data_pkt()
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':'will go into set_to_default function'})
        self.dev.set_to_default(pwr_rst=True)
        print('finished set to default plant configuration.')
        if self.debug: input('finished set to default plant configuration.\n pls press enter:')
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':'begin testing'})
        for item_reminder in self.dev.predefine.get('manual_check'):
            input(item_reminder)

        if len(test_item) == 0:
            for idx,i in enumerate(self.test_case):
                self.dev.driver.send_wakeup_msg()
                try:
                    if i[0] in self.dev.predefine.get('exclude_list'): 
                        # not running the test function which in exclude list
                        self.test_file.write([i[0], 'N/A-exclude', 'N/A-exclude'])                
                    if idx > (start_idx-2) and (i[0] not in self.dev.predefine.get('exclude_list')):
                        print(i[0], 'idx:', idx, 'src:', hex(self.dev.src))
                        if self.debug: eval('input([k, i])', {'k':sys._getframe().f_code.co_name, 'i':str(i[0]) + ' idx: ' + str(idx) + ' src: ' + hex(self.dev.src)})
                        if i[1] != 'manual' and i[1] != '':
                            eval(i[2], {'self':self, 'item':i[0],'targetdata':i[3], 'key':i[1]})    
                        elif i[1] == 'manual':
                            eval(i[2], {'self':self, 'item':i[0], 'sp':i[3], 'other_type':i[1]})  
                        else:
                            eval(i[2], {'self':self, 'item':i[0]})
                except Exception as e:
                    print(e, idx, i)
                    self.test_file.write([i[0], 'N/A-exception', 'N/A-exception'])
        else:
            for idx,i in enumerate(self.test_case):
                if i[0] in test_item:
                    print(i[0], 'idx:', idx, ' src: ', hex(self.dev.src))
                    if self.debug: eval('input([k, i])', {'k':sys._getframe().f_code.co_name, 'i':str(i[0]) + ' idx: ' + str(idx) + ' src: ' + hex(self.dev.src)})   # row = self.test_items.index(i[0]) + self.test_start_row
                    if i[1] != 'manual' and i[1] != '':
                        eval(i[2], {'self':self, 'item':i[0],'targetdata':i[3], 'key':i[1]})    
                    elif i[1] == 'manual':
                        eval(i[2], {'self':self, 'item':i[0], 'sp':i[3], 'other_type':i[1]})  
                    else:
                        eval(i[2], {'self':self, 'item':i[0]})  

    def init_test_dict(self): # ['item', 'function', 'target']
        '''
        add functions to test_case list, which include: sequency number of test item, function name, 
        exacuatable sentence and input values.
        '''
        self.test_case.append(['1.1', 'test_ecu_id', 'self.test_file.write([item, self.test_ecu_id(targetdata), self.function_measure_data[key]])', '83'])
        self.test_case.append(['1.2', 'test_ecu_id', 'self.test_file.write([item, self.test_ecu_id(targetdata), self.function_measure_data[key]])', '83'])
        self.test_case.append(['1.3', 'get_dev_src', 'self.test_file.write([item, self.get_dev_src(targetdata), self.function_measure_data[key]])', '0x80'])
        self.test_case.append(['1.4', 'get_addr_claim', 'self.test_file.write([item, self.get_addr_claim(targetdata), self.function_measure_data[key]])', '83'])
        self.test_case.append(['1.5', 'verify_addr_saved', 'self.test_file.write([item, self.verify_addr_saved(targetdata), self.function_measure_data[key]])', '0x87'])
        self.test_case.append(['1.6', 'manual', 'self.test_file.write([item])', ''])
        self.test_case.append(['1.7', 'manual', 'self.test_file.write([item])', ''])
        # self.test_case.append(['1.6', 'verify_addr_saved_uart', 'self.test_file.write([item, self.verify_addr_saved_uart(targetdata), self.function_measure_data[key]])', '0x87'])
        # self.test_case.append(['1.7', 'verify_addr_saved_uart', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['2', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['2.1', 'manual', 'self.test_file.write([item, sp, other_type])', ''])
        self.test_case.append(['2.2', 'manual', 'self.test_file.write([item, sp, other_type])', ''])
        self.test_case.append(['2.3', 'manual', 'self.test_file.write([item, sp, other_type])', ''])
        self.test_case.append(['2.4', 'manual', 'self.test_file.write([item, sp, other_type])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['3', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['3.1', 'test_pkt_rate', 'self.test_file.write([item, self.test_pkt_rate(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['3.2', 'test_pkt_type', 'self.test_file.write([item, self.test_pkt_type(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['3.3', 'test_lpf_rate', 'self.test_file.write([item, self.test_lpf_rate(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['3.4', 'test_lpf_acc', 'self.test_file.write([item, self.test_lpf_acc(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['3.5', 'test_orientation', 'self.test_file.write([item, self.test_orientation(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['3.6', 'test_unit_behavior', 'self.test_file.write([item, self.test_unit_behavior(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['3.7', 'test_fw_version', 'self.test_file.write([item, self.test_fw_version(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['3.8', 'test_ecu_id', 'self.test_file.write([item, self.test_ecu_id(targetdata), self.function_measure_data[key]])', '83'])
        self.test_case.append(['3.9', 'test_sensor_status', 'self.test_file.write([item, self.test_sensor_status(targetdata), self.function_measure_data[key]])', [0]])
        self.test_case.append(['3.10', 'test_sw_bit', 'self.test_file.write([item, self.test_sw_bit(targetdata), self.function_measure_data[key]])', '0x000000'])
        self.test_case.append(['3.11', 'test_hw_bit', 'self.test_file.write([item, self.test_hw_bit(targetdata), self.function_measure_data[key]])', '0x0000'])
        self.test_case.append(['3.12', 'test_algo_ctl', 'self.test_file.write([item, self.test_algo_ctl(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['4', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['4.1', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['4.1.1', 'test_fw_version', 'self.test_file.write([item, self.test_fw_version(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.1.2', 'test_pkt_rate', 'self.test_file.write([item, self.test_pkt_rate(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.1.3', 'test_pkt_type', 'self.test_file.write([item, self.test_pkt_type(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.1.4', 'test_lpf', 'self.test_file.write([item, self.test_lpf(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.1.5', 'test_orientation', 'self.test_file.write([item, self.test_orientation(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.1.6', 'test_ecu_id', 'self.test_file.write([item, self.test_ecu_id(targetdata), self.function_measure_data[key]])', '83'])
        self.test_case.append(['4.1.7', 'test_hw_bit', 'self.test_file.write([item, self.test_hw_bit(targetdata), self.function_measure_data[key]])', '0x0000'])
        self.test_case.append(['4.1.8', 'test_sw_bit', 'self.test_file.write([item, self.test_sw_bit(targetdata), self.function_measure_data[key]])', '0x000000'])
        self.test_case.append(['4.1.9', 'test_sensor_status', 'self.test_file.write([item, self.test_sensor_status(targetdata), self.function_measure_data[key]])', ['0x0000']])
        self.test_case.append(['4.1.10', 'test_unit_behavior', 'self.test_file.write([item, self.test_unit_behavior(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.1.11', 'test_algo_ctl', 'self.test_file.write([item, self.test_algo_ctl(targetdata), self.function_measure_data[key]])', ''])
        # self.test_case.append(['4.1.10', 'test_unit_behavior', 'self.test_file.write([item, self.test_unit_behavior(targetdata), self.function_measure_data[key]])', ''])
        # self.test_case.append(['4.1.10', 'test_unit_behavior', 'self.test_file.write([item, self.test_unit_behavior(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.2', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['4.2.1', 'test_save_config', 'self.test_file.write([item, self.test_save_config(targetdata), self.function_measure_data[key]])', '0x010001'])
        self.test_case.append(['4.2.2', 'test_algo_rst', 'self.test_file.write([item, self.test_algo_rst(targetdata), self.function_measure_data[key]])', '0x010001'])
        self.test_case.append(['4.2.3', 'set_pkt_rate', 'self.test_file.write([item, self.set_pkt_rate(targetdata), self.function_measure_data[key]])', '0x05'])
        self.test_case.append(['4.2.4', 'set_pkt_type', 'self.test_file.write([item, self.set_pkt_type(targetdata), self.function_measure_data[key]])', '0x0F'])
        self.test_case.append(['4.2.5', 'set_lpf_filter', 'self.test_file.write([item, self.set_lpf_filter(targetdata), self.function_measure_data[key]])', '0x0505'])
        self.test_case.append(['4.2.6', 'set_orientation', 'self.test_file.write([item, self.set_orientation(targetdata), self.function_measure_data[key]])', '0x0009'])
        self.test_case.append(['4.2.7', 'set_unit_behavior', 'self.test_file.write([item, self.set_unit_behavior(targetdata), self.function_measure_data[key]])', [222, 129]])
        self.test_case.append(['4.2.8', 'set_bank_ps0', 'self.test_file.write([item, self.set_bank_ps0(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.2.9', 'set_algo_ctl', 'self.test_file.write([item, self.set_algo_ctl(targetdata), self.function_measure_data[key]])', '00E803E8031400'])
        self.test_case.append(['4.2.10', 'set_bank_ps1', 'self.test_file.write([item, self.set_bank_ps1(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['4.3', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['4.3.1', 'set_pkt_type', 'self.test_file.write([item, self.set_pkt_type(targetdata, type_measure=True), self.function_measure_data[key]])', '0x3F'])
        self.test_case.append(['4.3.2', 'set_pkt_type', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['4.3.3', 'set_pkt_type', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['4.3.4', 'set_pkt_type', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['4.3.5', 'set_pkt_type', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['4.3.6', 'set_pkt_type', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.1.1', 'set_pkt_rate', 'self.test_file.write([item, self.set_pkt_rate(targetdata, saved_rst=True), self.function_measure_data[key]])', '0x05'])
        self.test_case.append(['5.1.2', 'set_pkt_type', 'self.test_file.write([item, self.set_pkt_type(targetdata, saved_rst=True), self.function_measure_data[key]])', '0x0F'])
        self.test_case.append(['5.1.3', 'set_lpf_filter', 'self.test_file.write([item, self.set_lpf_filter(targetdata, saved_rst=True), self.function_measure_data[key]])', '0x0505'])
        self.test_case.append(['5.1.4', 'set_orientation', 'self.test_file.write([item, self.set_orientation(targetdata, saved_rst=True), self.function_measure_data[key]])', '0x0009'])
        self.test_case.append(['5.1.5', 'set_unit_behavior', 'self.test_file.write([item, self.set_unit_behavior(targetdata, saved_rst=True), self.function_measure_data[key]])', [222, 129]])
        self.test_case.append(['5.1.6', 'set_algo_ctl', 'self.test_file.write([item, self.set_algo_ctl(targetdata, saved_rst=True), self.function_measure_data[key]])', '00E803E8031400'])
        self.test_case.append(['5.1.7', 'set_hw_bit_ps', 'self.test_file.write([item, self.set_hw_bit_ps(targetdata, saved_rst=True), self.function_measure_data[key]])', '0x0000'])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.2.1', 'set_pkt_rate', 'self.test_file.write([item, self.set_pkt_rate(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x01'])
        self.test_case.append(['5.2.2', 'set_pkt_type', 'self.test_file.write([item, self.set_pkt_type(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x07'])
        self.test_case.append(['5.2.3', 'set_lpf_filter', 'self.test_file.write([item, self.set_lpf_filter(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x1905'])
        self.test_case.append(['5.2.4', 'set_orientation', 'self.test_file.write([item, self.set_orientation(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x0000'])
        self.test_case.append(['5.2.5', 'set_unit_behavior', 'self.test_file.write([item, self.set_unit_behavior(targetdata, nosaved_rst=True), self.function_measure_data[key]])', [222, 129]])
        self.test_case.append(['5.2.6', 'set_algo_ctl', 'self.test_file.write([item, self.set_algo_ctl(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '00E803E8031400'])
        self.test_case.append(['5.2.7', 'set_hw_bit_ps', 'self.test_file.write([item, self.set_hw_bit_ps(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x0000'])        
        # self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        # self.test_case.append(['5.2.1', 'try_set_list_nosc', 'self.test_file.write([item, self.try_set_list_nosc(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x01'])
        # self.test_case.append(['5.2.2', 'try_set_list_nosc', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        # self.test_case.append(['5.2.3', 'try_set_list_nosc', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        # self.test_case.append(['5.2.4', 'try_set_list_nosc', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        # self.test_case.append(['5.2.5', 'try_set_list_nosc', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        # self.test_case.append(['5.2.6', 'set_hw_bit_ps', 'self.test_file.write([item, self.set_hw_bit_ps(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x0000'])
        # self.test_case.append(['5.2.7', 'set_unit_bhr_rawrate', 'self.test_file.write([item, self.set_unit_bhr_rawrate(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '0x01'])
        # self.test_case.append(['5.2.8', 'set_algo_ctl', 'self.test_file.write([item, self.set_algo_ctl(targetdata, nosaved_rst=True), self.function_measure_data[key]])', '00E803E8031400'])        
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.3.1', 'try_rate_list', 'self.test_file.write([item, self.try_rate_list(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.2', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.3', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.4', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.5', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.6', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.7', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.8', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.3.9', 'try_rate_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.4.1', 'try_type_list', 'self.test_file.write([item, self.try_type_list(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.2', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.3', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.4', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.5', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.6', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.7', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.8', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.9', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.10', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.11', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.12', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.13', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.14', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.15', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.16', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.17', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.4.18', 'try_type_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])        
        self.test_case.append(['5.5.1', 'try_lpf_list', 'self.test_file.write([item, self.try_lpf_list(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['5.5.2', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.5.3', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.5.4', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.5.5', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.5.6', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.5.7', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.5.8', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.6.1', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.6.2', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.6.3', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.6.4', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.6.5', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.6.6', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.6.7', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.6.8', 'try_lpf_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.7', 'try_orient_list', 'self.test_file.write([item, self.try_orient_list(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.8.1', 'try_unit_bhr_list', 'self.test_file.write([item, self.try_unit_bhr_list(targetdata), self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.2', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.3', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.4', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.5', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.6', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.7', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.8', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.9', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.10', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.11', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.12', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.13', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.14', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.15', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.16', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.17', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.18', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.19', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.20', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.8.21', 'try_unit_bhr_list', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['5.9.1', 'set_try_ps', 'self.test_file.write([item, self.set_try_ps(), self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.2', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.3', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.4', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.5', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.6', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.7', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.8', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.9', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])    
        self.test_case.append(['5.9.10', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.11', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.12', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', ''])
        self.test_case.append(['5.9.13', 'set_try_ps', 'self.test_file.write([item, self.function_measure_data[key], self.function_measure_data[key]])', '']) 
        self.test_case.append(['', '', 'self.test_file.write([item])', ''])
        self.test_case.append(['6', 'test_save_file', 'self.test_file.write([item, self.test_save_file(targetdata), self.function_measure_data[key]])', ''])

    def test_ecu_id(self, target_data): # 1.1, 1.2, 3.8 4.1.6
        '''
        get ecu_id by send request cmd, to check whether target_data in it or not
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        feedback = self.dev.request_cmd('ecu_id').upper() 
        measure_data = "0x{0}".format(feedback)     
        # save function result to function_measure_data dict, 
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return target_data in measure_data

    def get_dev_src(self, target_data): # 1.3        
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        feedback = self.dev.src
        measure_data = "{0:#x}".format(feedback)
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def get_addr_claim(self, target_data): # 1.4
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        self.dev.set_to_default(pwr_rst = True)
        feedback = self.dev.get_payload_auto(auto_name = 'addr')
        measure_data = "0x{0}".format(feedback)
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return target_data in measure_data

    def verify_addr_saved(self, target_data): # 1.5 
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        self.dev.set_cmd('set_unit_behavior', self.dev.default_confi['unit_behavior'] + [0, 0, int(target_data, 16)])
        time.sleep(0.2)
        self.dev.set_cmd('save_config', [2]) # save and power reset
        time.sleep(1)
        addr_in = int(target_data, 16) in self.dev.driver.get_can_nodes()
        self.function_measure_data[sys._getframe().f_code.co_name] = addr_in
        self.dev.driver.send_can_msg(id = 0x18FF5900, data = [int(target_data, 16)] + self.dev.default_confi['unit_behavior'] + [0, 0, 0x80])
        time.sleep(0.2)
        self.dev.driver.send_can_msg(id = 0x18FF5900, data = [int(target_data, 16)] + self.dev.default_confi['unit_behavior'] + [0, 0, 0x80])
        time.sleep(0.2)
        self.dev.driver.send_can_msg(id = 0x18FF5100, data = [2, 0x87]) # save and power reset
        time.sleep(0.2)
        self.dev.driver.send_can_msg(id = 0x18FF5100, data = [2, 0x87]) # save and power reset
        time.sleep(1)
        self.dev.driver.send_wakeup_msg()
        return addr_in

    def verify_addr_saved_uart(self, target_data): #1.6-1.7 0x87
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        input('is {0} connect with /dev/ttyUSB0, right? y/n?'.format(hex(self.dev.src)))
        # get current address saved in EEPROM
        addr_list = self.dev.send_get_uart_msg(request_data = [0x55, 0x55, 0x52, 0x46, 0x03, 0x01, 0x00, 0x32, 0xac, 0xfa]) # 5555 5246 03 010032 acfa read 0x32 from EEPROM
        while addr_list[0] != '5246':
            addr_list = self.dev.send_get_uart_msg(request_data = [0x55, 0x55, 0x52, 0x46, 0x03, 0x01, 0x00, 0x32, 0xac, 0xfa]) # 5555 5246 03 010032 acfa read 0x32 from EEPROM
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':addr_list})
        original = int(addr_list[2][-4:], 16)
        #change addr and saved
        self.dev.set_cmd('set_unit_behavior', self.dev.default_confi['unit_behavior'] + [0, 0, int(target_data, 16)])
        time.sleep(0.2)
        self.dev.set_cmd('save_config', [2]) # save and power reset
        time.sleep(2)
        #check new value by uart
        self.dev.send_get_uart_msg(request_data = [0x55, 0x55, 0x52, 0x46, 0x03, 0x01, 0x00, 0x32, 0xac, 0xfa])
        time.sleep(0.1)
        self.dev.send_get_uart_msg(request_data = [0x55, 0x55, 0x52, 0x46, 0x03, 0x01, 0x00, 0x32, 0xac, 0xfa])
        addr_newlist = ['','','','']
        while addr_newlist[0] != '5246':
            addr_newlist = self.dev.send_get_uart_msg(request_data = [0x55, 0x55, 0x52, 0x46, 0x03, 0x01, 0x00, 0x32, 0xac, 0xfa]) # 5555 5246 03 010032 acfa read 0x32 from EEPROM to get SA
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':addr_newlist})
        new = int(addr_newlist[2][-4:], 16)

        self.function_measure_data[sys._getframe().f_code.co_name] = (new == int(target_data, 16))

        # back to original address
        self.dev.driver.send_can_msg(0x18FF5900, [new, 146, 0, 0, 0, original])
        time.sleep(0.2)
        self.dev.driver.send_can_msg(0x18FF5100, [2, new]) # save and power reset
        time.sleep(2)
        self.dev.driver.send_wakeup_msg()
        # self.dev.set_cmd('set_unit_behavior', [self.dev.predefine.get('unit_behavior'), 0, 0, 0, int(target_data, 16)])

        return new == int(target_data, 16)
        
    # 1.6 - 2.3 need to be realized

    def test_pkt_rate(self, target_data): # 3.1 4.1.2
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['pkt_rate'])
        payload = self.dev.request_cmd('pkt_rate')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-2:]
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def test_pkt_type(self, target_data, len_fb_bytes = 2): # 3.2 4.1.3
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['pkt_type'])
        payload = self.dev.request_cmd('pkt_type')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload

        feedback = payload[-4:]
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':['fb_byte:', feedback]}) 
        feedback = hex(struct.unpack('<h', bytes.fromhex(feedback))[0])[2:]
        measure_data = "0x{0}".format(feedback)  
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def test_lpf_rate(self, target_data): # 3.3
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['lpf_filter'][0])
        payload = self.dev.request_cmd('lpf_filter')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:-2] 
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def test_lpf_acc(self, target_data): # 3.4
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['lpf_filter'][1])
        payload = self.dev.request_cmd('lpf_filter')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-2:] 
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def test_orientation(self, target_data): # 3.5 4.1.5
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['orientation'][0] * 256 + self.dev.default_confi['orientation'][1])
        payload = self.dev.request_cmd('orientation')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:] 
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def test_unit_behavior(self, target_data, len_fb_bytes = 2): # 3.6, 4.1.10
        '''
        check unit behavior is same with predefine.get('unit_behavior')/tartet data value or not
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = self.dev.predefine.get('unit_behavior')
        target_data_val = target_data[0] * 256 + target_data[1]
        payload = self.dev.request_cmd('unit_behavior')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload        
        feedback = payload[2:]
        # feedback = payload[-2:]    # & bitmask: 0x3F 
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[measure_data]})
        return int(measure_data, 16) == target_data_val
    
    def test_fw_version(self, target_data): # 3.7, 4.1.1
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        payload = self.dev.request_cmd('fw_version')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-10:] 
        # fw_str = '.'.join([payload[:2], payload[2:4], payload[4:6], payload[6:8], payload[8:10]])
        measure_data = "0x{0}".format(feedback)
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == self.fw_num

    def test_algo_ctl(self, target_data): # 3.12 4.1.12 Check last 6 bytes is same as defaut value
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = self.dev.default_confi['algo_ctl']
        payload = self.dev.request_cmd('algo_ctl')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        # feedback = payload[4:6] 
        # measure_data = "0x{0}".format(feedback)     
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[payload, target_data]})
        self.function_measure_data[sys._getframe().f_code.co_name] = payload  
        return target_data[2:].upper() in payload.upper()
    
    def test_lpf(self, target_data): # 4.1.4
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['lpf_filter'][0]*256 + self.dev.default_confi['lpf_filter'][1])
        payload = self.dev.request_cmd('lpf_filter')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:] 
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)
    
    def test_hw_bit(self, target_data): # 4.1.7
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        payload = self.dev.request_cmd('hw_bit')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:] 
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def test_sw_bit(self, target_data): # 4.1.8
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        payload = self.dev.request_cmd('sw_bit')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:]
        measure_data = "0x{0}".format(feedback)
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data
        return int(measure_data, 16) == int(target_data, 16)

    def test_sensor_status(self, target_data): # 4.1.9
        '''
        In case you receive 0x8004 – “attitude only” algorithm is running
        In case you receive 0x8006 – “attitude only” algorithm is running with “high gain”.
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        payload = self.dev.request_cmd('status')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[:] 
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':measure_data})
        return int(measure_data, 16) in target_data

    def test_save_config(self, target_data): # 4.2.1
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        feedback = self.dev.set_get_feedback_payload(set_fb_name = 'save_config_feedback')
        if feedback == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = feedback
            return feedback
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def test_algo_rst(self, target_data): # 4.2.2
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        feedback = self.dev.set_get_feedback_payload(set_fb_name = 'algo_rst_feedback')
        if feedback == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = feedback
            return feedback

        measure_data = "0x{0}".format(feedback)
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)
    
    def try_set_list_nosc(self, target_data, saved_rst = False, nosaved_rst = False): # 5.2.1-5.2.5
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        nosc_set = True
        self.dev.set_cmd('set_pkt_rate', [5])
        time.sleep(0.2)
        self.dev.set_cmd('set_pkt_type', [0xF])
        time.sleep(0.2)
        self.dev.set_cmd('set_lpf_filter', [5, 5])
        time.sleep(0.2)
        self.dev.set_cmd('set_orientation', [0, 9])
        time.sleep(0.2)        
        self.dev.set_cmd('set_unit_behavior', [4, 1, 0, 0, self.dev.src])
        time.sleep(0.2)

        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(1)
            self.dev.driver.send_wakeup_msg() 

        payload = self.dev.request_cmd('pkt_rate')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-2:]
        if int(feedback, 16) != self.dev.default_confi['pkt_rate']:
            nosc_set = False
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':nosc_set})

        payload = self.dev.request_cmd('pkt_type')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        len_fb_bytes = self.dev.get_item_json('pkt_type')['fb_length']
        feedback = payload[-(len_fb_bytes-1)*2:]    
        if len(feedback) == 4:      
            feedback = hex(struct.unpack('<h', bytes.fromhex(feedback))[0])[2:] # '0x5' so, need to get data from position2, ignore '0x'
        if len(feedback) == 2: 
            feedback = hex(struct.unpack('B', bytes.fromhex(feedback))[0])[2:]
        if int(feedback, 16) != self.dev.default_confi['pkt_type']:
            nosc_set = False

        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':nosc_set})
        payload = self.dev.request_cmd('lpf_filter')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:]
        lpf_list = self.dev.predefine.get('lpf_filter')
        if int(feedback, 16) != (lpf_list[0] * 256 + lpf_list[1]): # hex(self.dev.predefine.get('lpf_filter')[0])
            nosc_set = False

        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':nosc_set})
        payload = self.dev.request_cmd('orientation')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:]
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[nosc_set, feedback, self.dev.default_confi['orientation']]})
        def_ori = self.dev.default_confi['orientation']
        if int(feedback, 16) != int(def_ori[0] * 256 + def_ori[1]):
            nosc_set = False

        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':nosc_set})
        payload = self.dev.request_cmd('unit_behavior')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload        
        feedback = payload[2:]  
        if self.dev.decode_behavior_num(int(feedback[:2], 16))[2] == 1:
                nosc_set = False
        if self.dev.decode_behavior_num(int(feedback[2:], 16))[0] == 1:
                nosc_set = False

        self.function_measure_data[sys._getframe().f_code.co_name] = nosc_set
        self.dev.set_to_default(pwr_rst = False)
        return nosc_set

    def set_pkt_rate(self, target_data, saved_rst = False, nosaved_rst = False): # 4.2.3 5.1.1 5.2.1
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['pkt_rate'])
        self.dev.set_cmd('set_pkt_rate', [int(target_data, 16)])
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(2)
        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(2)  
            target_data = hex(self.dev.default_confi['pkt_rate']) # if no save repower, target data should be update to default value
            self.dev.driver.send_wakeup_msg() 

        payload = self.dev.request_cmd('pkt_rate')
        time.sleep(0.2)
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':payload})

        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-2:]
        self.dev.set_to_default(pwr_rst = False)
        measure_data = "0x{0}".format(feedback) 
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def set_pkt_type(self, target_data, saved_rst = False, nosaved_rst = False, type_measure = False): # 4.2.4 4.3.1-4.3.4 5.1.2 5.2.2
        '''
        target_data: such as '0x07' '0x3F'
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['pkt_type'])
        self.dev.set_cmd('set_pkt_type', [int(target_data, 16)])
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(2)
        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(2)
            target_data = hex(self.dev.default_confi['pkt_type']) # if no save repower, target data should be update to default value
            self.dev.driver.send_wakeup_msg()

        payload = self.dev.request_cmd('pkt_type')
        time.sleep(0.2)
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        if self.dev.get_item_json('pkt_type')['fb_length'] == 2:
            len_fb_bytes = 2
            feedback = payload[-(len_fb_bytes-1)*2:]
        elif self.dev.get_item_json('pkt_type')['fb_length'] == 3:
            len_fb_bytes = 3
            feedback = payload[-(len_fb_bytes-1)*2:]
            feedback = hex(struct.unpack('<h', bytes.fromhex(feedback))[0])[2:]
        # feedback = payload[-2:]
        measure_data = "0x{0}".format(feedback)
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data 
        if type_measure:
            types_data = len(self.dev.predefine.get('types_name'))
            # default_data = hex(pow(2, types_data) - 1) # this is default num
            pkt_type_mea = self.dev.measure_pkt_type(type_num=types_data)
            self.function_measure_data[sys._getframe().f_code.co_name] = pkt_type_mea
            if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[measure_data, types_data, pkt_type_mea]})
            if pkt_type_mea != int(target_data, 16):
                return False
        self.dev.set_to_default(pwr_rst = False)
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[target_data, measure_data]})
        if int(measure_data, 16) != int(target_data, 16):
            return False
        return True

    def set_lpf_filter(self, target_data, saved_rst = False, nosaved_rst = False): # 4.2.5 5.1.3 5.2.3
        '''
        target_data: such as '0x1905' '0x0505'
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        if target_data.strip() == '':
            target_data = hex(self.dev.default_confi['lpf_filter'][0]*256 + self.dev.default_confi['lpf_filter'][1])
        self.dev.set_cmd('set_lpf_filter', [int(target_data, 16) >> 8, int(target_data, 16) & 0x00FF])
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(2)
        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(2)
            target_data = hex(self.dev.default_confi['lpf_filter'][0]*256 + self.dev.default_confi['lpf_filter'][1]) # if no save repower, target data should be update to default value
            self.dev.driver.send_wakeup_msg() 

        payload = self.dev.request_cmd('lpf_filter')
        time.sleep(0.2)
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:]
        time.sleep(1)
        self.dev.set_to_default(pwr_rst = False)
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def set_orientation(self, target_data, saved_rst = False, nosaved_rst = False): # 4.2.6 5.1.4 5.2.4
        '''
        target_data: such as '0x0000' '0x0165'
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        self.dev.set_cmd('set_orientation', [int(target_data, 16) >> 8, int(target_data, 16) & 0x00FF])
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(1)
        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(1)
            target_data = hex(self.dev.default_confi['set_orientation'][0]*256 + self.dev.default_confi['set_orientation'][1]) # if no save repower, target data should be update to default value
            self.dev.driver.send_wakeup_msg() 

        payload = self.dev.request_cmd('orientation')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[-4:] 
        self.dev.set_to_default(pwr_rst = False)
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        return int(measure_data, 16) == int(target_data, 16)

    def set_unit_behavior(self, target_data, disable_bit = [0, 0], saved_rst = False, nosaved_rst = False): # 4.2.7 5.1.5 5.2.5 invalid now, replaced by set unit behavior new().
        '''
        target_data: such as [222, 129], it is string of enable_bit
        '''
        self.dev.set_to_default(pwr_rst = True)
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        default_data = self.dev.default_confi['unit_behavior']
        if len(target_data) == 0:
            target_data = self.dev.default_confi['unit_behavior']
            target_data_val = target_data[0] * 256 + target_data[1] 
        else:
            # target_data = [default_data[0] + 4, default_data[1] + 1]
            target_data_val = target_data[0] * 256 + target_data[1]     
        self.dev.set_cmd('set_unit_behavior', target_data + disable_bit + [self.dev.src])
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('set_unit_behavior', target_data + disable_bit + [self.dev.src])
            time.sleep(0.2)
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(1)
        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(1)
            self.dev.driver.send_wakeup_msg()            
            target_data_val = default_data[0] * 256 + default_data[1] # if no save repower, target data should be update to default value

        payload = self.dev.request_cmd('unit_behavior')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        feedback = payload[2:]        
 
        self.dev.set_to_default(pwr_rst = False)
        # if self.debug: eval('print(k, i, j, m, n, h)', {'k':sys._getframe().f_code.co_name,'i':feedback, 'j':original_behavior, 'm':enabel_bit, 'n':target_behavior, 'h':disable_bit})
        measure_data = "0x{0}".format(feedback)
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[target_data_val, feedback, measure_data]})
        return int(measure_data, 16) == target_data_val

    def set_unit_behavior_new(self, targetdata, saved_rst = False, nosaved_rst = False): # 4.2.7 5.1.5 #5.2.5     
        '''
        target is not used, for bytes1-2 we set bit2 and bit0 to 1, to check it.
        '''   
        self.dev.set_to_default(pwr_rst = True)
        set_unit_bhr = True
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        if self.test_unit_behavior(target_data = ''): # check default is right, then go on
            # set unit value to what we want
            bit_idx = 2 # start from 0, set bit2 to 1 in unit behavior byte1. not use targetdata
            enable_val = self.dev.predefine.get('unit_behavior') + pow(2, bit_idx)  #it is unit behavior byte1    
            bit_idx_rawrate = 0 # start from 0, set bit0 to 1 in unit behavior byte2. not use targetdata      
            enable_val_rawrate = self.dev.predefine.get('unit_behavior2') + pow(2, bit_idx_rawrate) #it is unit behavior byte2
            if self.dev.type_name == 'MTLT305D' or self.dev.type_name == 'MTLT335_NEW':
                self.dev.set_cmd('set_unit_behavior', [enable_val, enable_val_rawrate, 0, 0, self.dev.src])                
            elif self.dev.type_name == 'MTLT335':
                self.dev.set_cmd('set_unit_behavior', [enable_val])
            time.sleep(1)
            # restart if need
            if saved_rst == True:
                self.dev.set_cmd('save_config', [2]) # save and restart
                time.sleep(1)
            if nosaved_rst == True:
                if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                    self.dev.auto_power.power_off()
                    time.sleep(4)
                    self.dev.auto_power.power_on()
                else:
                    self.dev.set_cmd('algo_rst', [2]) # no save reset
                    # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                    #     pass
                time.sleep(1)
                self.dev.driver.send_wakeup_msg() 

            # check value is as expected or not
            if self.test_unit_behavior(target_data = hex(enable_val)) == False or self.test_unit_bhr_rawrate(hex(enable_val_rawrate)) == False:
                set_unit_bhr = False
            self.function_measure_data[sys._getframe().f_code.co_name] = self.function_measure_data.get('test_unit_behavior')  
        else:
            set_unit_bhr = False
            test_value = self.function_measure_data.get('test_unit_behavior')
            print(f'unit default value is not right, measure value:{test_value}')
            self.function_measure_data[sys._getframe().f_code.co_name] = set_unit_bhr  
        
        return set_unit_bhr

    def set_bank_ps0(self, target_data, saved_rst = False, algo_rst=0x60, hw_bit=0x52, sw_bit=0x53, status_bit=0x54, hr_acc=0x6C): # 4.2.8
        '''
        target_data: such as '0x0000' '0x0165'
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        # algo_rst, hw_bit, sw_bit, status_bit, hr_acc = 0x60, 0x52, 0x53, 0x54, 0x6C
        data = [algo_rst, 0, hw_bit, sw_bit, status_bit, hr_acc]
        self.dev.set_cmd('set_bank_ps0', data)
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(1)
        feedback = self.dev.set_get_feedback_payload(set_fb_name = 'algo_rst_feedback')
        self.dev.set_to_default(pwr_rst = False)
        if feedback == False:
            self.function_measure_data[sys._getframe().f_code.co_name] = True  
            return True
        else:
            self.function_measure_data[sys._getframe().f_code.co_name] = False
            return False

    def set_bank_ps1(self, target_data, saved_rst = False): # 4.2.8
        '''
        target_data: such as '0x0000' '0x0165'
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        self.dev.set_to_default()
        time.sleep(3)
        pkt_rate, pkt_type, dig_filter, ori_request, unit_bhr, algo_ctl = 0x60, 0x56, 0x57, 0x58, 0x59, 0x5B
        if self.dev.type_name == 'MTLT305D':
            data = [pkt_rate, pkt_type, dig_filter, ori_request, unit_bhr, algo_ctl, 0]
        if self.dev.type_name == 'MTLT335':
            data = [pkt_rate, pkt_type, dig_filter, ori_request, unit_bhr, algo_ctl, 0]
        self.dev.set_cmd('set_bank_ps1', data)
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(1)
        feedback = self.dev.request_cmd('pkt_rate') 
        time.sleep(0.2)
        self.dev.set_to_default(pwr_rst = False)
        if feedback == False:
            self.function_measure_data[sys._getframe().f_code.co_name] = True  
            return True
        else:
            self.function_measure_data[sys._getframe().f_code.co_name] = False
            return False           

    def set_algo_ctl(self, target_data, saved_rst = False, nosaved_rst = False): # 4.2.10 5.1.8 5.2.8 Check last 6 bytes is same as set value
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        # data = [0x0, 0xE8, 0x03, 0xE8, 0x03, 0x14, 0x0]   #enable raw rate in unit behavior
        self.dev.set_to_default()
        time.sleep(3)
        data = [int(target_data[x:x+2], 16) for x in range(0,13,2)]
        self.dev.set_cmd('set_algo_ctl', data)
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(1)
        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(2)  
            target_data = self.dev.default_confi['algo_ctl'] # if no save repower, target data should be update to default value
            self.dev.driver.send_wakeup_msg() 
        payload = self.dev.request_cmd('algo_ctl')
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload
        # feedback = payload[4:6] 
        # measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = payload  
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[target_data, payload]})
        return target_data[2:].upper() in payload.upper()

    def set_try_ps(self, newps = 0x60, pstype = None, tryidx = None): # 5.9.1-5.9.13
        '''
        try each ps by newps and check result is expected
        ps_type = 'set_bank_ps0', try_idx = 0 should be in try_idx list of json
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':hex(newps)})
        ps_type = ['set_bank_ps0', 'set_bank_ps1'] if pstype == None else [pstype]
        results = {}
        for i in ps_type:
            ps_dict = self.dev.predefine[i].get('ps_default')
            cmdname, psval = list(ps_dict.keys()), [int(x,16) for x in list(ps_dict.values())] # get all PS cmd names and PS num
            idx_list = self.dev.predefine[i].get('try_idx')
            try_idx = idx_list if tryidx == None else [tryidx]
            try:
                for j in try_idx:
                    # if False in list(results.values()):
                    #     break
                    if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[ps_type, i,j, idx_list, try_idx]})
                    cmd_name = cmdname[j] # list out of range
                    item_dict = self.dev.get_item_json(namestr = cmd_name)
                    if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[results, cmd_name, item_dict, [hex(x) for x in psval]]})
                    self.dev.set_cmd(i, psval[:j] + [newps] + psval[j+1:])
                    time.sleep(0.2)
                    if item_dict.get('type') == 'set': # set cmd
                        feedback = self.dev.set_get_feedback_payload(set_fb_name = cmd_name + '_feedback')
                        feedback2 = self.dev.new_set_cmd(new_ps = newps, data = [0, self.dev.src])
                        if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[item_dict.get('type'), feedback, feedback2]})
                        if (feedback != False) or (feedback2 == False):
                            results[cmd_name] = False
                        else:
                            results[cmd_name] = True
                        if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[results, item_dict.get('type'), feedback, feedback2]})
                    elif item_dict.get('type') == 'request': # request cmd
                        feedback = self.dev.request_cmd(cmd_name)
                        feedback2 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + newps)
                        if (feedback != False) or (feedback2 == False):
                            results[cmd_name] = False
                        else:
                            results[cmd_name] = True
                        if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[results, item_dict.get('type'), feedback, feedback2]})                        
                    elif item_dict.get('type') == 'auto': # auto send data msg
                        feedback = self.get_msg(target_data=cmd_name,back_default=False)
                        feedback2 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + newps)
                        if (feedback != False) or (feedback2 == False):
                            results[cmd_name] = False
                        else:
                            results[cmd_name] = True
                        if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':[results, item_dict.get('type'), feedback, feedback2]})
                    else:
                        print(f'no this type cmd or msg in function {sys._getframe().f_code.co_name}') 

                    if self.debug or (False in list(results.values())): eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[i, j, results, cmd_name, item_dict, item_dict.get('type')]}) 
            except Exception as e:
                print(e, i, j, item_dict, feedback, feedback2)
        final_reslut = False if False in list(results.values()) else True
        if self.debug or (final_reslut == False): eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':results})
        self.function_measure_data[sys._getframe().f_code.co_name] = final_reslut
        return final_reslut         

    def get_msg(self, target_data='acc_hr', back_default = True): # 4.3.6
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        self.dev.set_cmd('set_pkt_type', [pow(2, len(self.dev.predefine.get('types_name'))) - 1])
        self.dev.set_cmd('set_pkt_rate', [1])
        self.dev.empty_data_pkt()
        time.sleep(0.5)        
        feedback = self.dev.get_payload_auto(auto_name = target_data)
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':feedback})
        if back_default: self.dev.set_to_default(pwr_rst = True)
        time.sleep(0.2)
        if feedback != False:
            self.function_measure_data[sys._getframe().f_code.co_name] = True  
            return True
        else:
            self.function_measure_data[sys._getframe().f_code.co_name] = False
            return False

    def set_hw_bit_ps(self, target_data, saved_rst = False, nosaved_rst = False): # 5.1.6 5.2.6
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        new_hw_bit = 0x60
        self.dev.set_cmd(cmd_name = 'set_bank_ps0', payload_without_src = [0x50, 0x51, new_hw_bit, 0x53, 0x54, 0x6B, 0x6D])
        time.sleep(0.2)
        if saved_rst == True:
            self.dev.set_cmd('save_config', [2]) # save and restart
            time.sleep(1)
        if nosaved_rst == True:
            if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
                self.dev.auto_power.power_off()
                time.sleep(4)
                self.dev.auto_power.power_on()
            else:
                self.dev.set_cmd('algo_rst', [2]) # no save reset
                # while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
                #     pass
            time.sleep(1)
            self.dev.driver.send_wakeup_msg() 
            if self.test_hw_bit(target_data='0x0000'):
                self.function_measure_data[sys._getframe().f_code.co_name] = self.function_measure_data['test_hw_bit'] 
                return True

        newpgn = (0xFF50 & 0xFF00) + new_hw_bit    
        payload = self.dev.new_request_cmd(src = self.dev.src, new_pgn = newpgn)
        # print(payload)
        if payload == False: 
            self.function_measure_data[sys._getframe().f_code.co_name] = payload
            return payload    
        feedback = payload[:2]
        measure_data = "0x{0}".format(feedback)     
        self.function_measure_data[sys._getframe().f_code.co_name] = measure_data  
        # print(self.dev.new_request_cmd(src = self.dev.src, new_pgn = newpgn))
        # time.sleep(0.2)
        # print(self.dev.new_request_cmd(src = self.dev.src, new_pgn = newpgn))
        return (int(measure_data, 16) & 0x7) == int(target_data, 16)

    def try_rate_list(self, target_data, actual_measure = True): # 5.3.1-5.3.9
        '''
        try_odr_list
        '''
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        rate_list   = [0, 1, 2, 4, 5, 10, 20, 25, 50] # [0, 1, 2, 4, 5, 10, 20, 25, 50]
        odr_set_ok = True
        for value in rate_list:
            if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':odr_set_ok})
            if odr_set_ok == False:
                break
            self.dev.set_cmd('set_pkt_rate', [value])   
            time.sleep(0.5)        
            if self.test_pkt_rate(target_data=hex(value)) == False:
                odr_set_ok = False
            if actual_measure == True:
                odr = 100/value if value != 0 else 0
                pass_delta = 20 if value < 4 else 1
                odr_mea = self.dev.measure_pkt_rate()
                if abs(odr_mea - odr) > pass_delta:
                    odr_set_ok = False 
            if self.debug or (odr_set_ok == False): eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[value, odr_set_ok]})    
        self.dev.set_to_default(pwr_rst = False)
        self.function_measure_data[sys._getframe().f_code.co_name] = odr_set_ok             

        return odr_set_ok

    def try_type_list(self, target_data, actual_measure = True): # 5.4.1-5.4.18
        # check all lpf configuration list is valid
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        types_data = len(self.dev.predefine.get('types_name'))
        if types_data == 6:
            type_list          = [0, 1, 2, 4, 7, 8, 0xB, 0xF, 0xE, 0x13, 0x16, 0x17, 0x1B, 0x1C, 0x1E, 0x1F, 0x2F, 0x3F] 
        elif types_data == 5:
            type_list          = [0, 1, 2, 4, 7, 8, 0xB, 0xF, 0xE, 0x13, 0x16, 0x17, 0x1B, 0x1C, 0x1E, 0x1F] 
        else:
            type_list          = [0, 1, 2, 4, 7, 8, 0xB, 0xF, 0xE, 0x13, 0x16, 0x17, 0x1B, 0x1C, 0x1E, 0x1F] 
            print("packet type use 5 number types")
        type_set_ok        = True
        
        for value in type_list:
            if value > (pow(2,types_data)-1): continue
            if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':type_set_ok})
            if type_set_ok == False:
                break
            self.dev.set_cmd('set_pkt_type', [value])
            time.sleep(0.5)
            if self.test_pkt_type(target_data=hex(value)) == False:
                type_set_ok = False
            if actual_measure == True:
                pkt_type_mea = self.dev.measure_pkt_type(type_num = types_data)
                if pkt_type_mea != value:
                    type_set_ok = False
            if self.debug or (type_set_ok == False): eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[value, type_set_ok]}) 
        self.dev.set_to_default(pwr_rst = False)
        self.function_measure_data[sys._getframe().f_code.co_name] = type_set_ok 
        return type_set_ok  

    def try_lpf_list(self, target_data): # 5.5.1-5.5.8 5.6.1-5.6.8
        # check all lpf configuration list is valid
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        lpf_list          = [0, 2, 5, 10, 20, 25, 40, 50] 
        lpf_set_ok        = True
        for value in lpf_list:
            if lpf_set_ok == False:
                break
            if self.set_lpf_filter(target_data = hex((value<<8) + value)) == False: 
                lpf_set_ok = False
            if self.debug or (lpf_set_ok == False): eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[value, lpf_set_ok]}) 
        self.dev.set_to_default(pwr_rst = False)
        self.function_measure_data[sys._getframe().f_code.co_name] = lpf_set_ok 

        return lpf_set_ok 

    def try_orient_list(self, target_data): # 5.7
        # check some orientation configuration items is valid
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        ori_list        = [0x0000, 0x0009, 0x0023, 0x002A, 0x0041, 0x0048, 0x0062, 0x006B, 
                            0x0085, 0x008C, 0x0092, 0x009B, 0x00C4, 0x00CD, 0x00D3, 0x00DA, 0x0111, 
                            0x0118, 0x0124, 0x012D, 0x0150, 0x0159, 0x0165, 0x016C] 
        # while input('Please place the unit horizontally to let program detect orientation configuraitons, is it horizontal placement, y/n ? ') != 'y':
        #     pass      
        ori_set_ok = True
        for idx,value in enumerate(ori_list):
            if self.set_orientation(target_data = hex(value)) == False:
                ori_set_ok = False
        self.dev.set_to_default(pwr_rst = False)
        self.function_measure_data[sys._getframe().f_code.co_name] = ori_set_ok 
        return ori_set_ok
    
    def try_unit_bhr_list(self, target_data):  # 5.8.1-5.8.21
        # check some behavior configuration items is set
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        self.dev.set_to_default()
        time.sleep(3)
        bhr_set_ok        = True
        bitsnum = self.dev.predefine['bits_unit_bhr']
        enable_list, disable_list = [pow(2, x) for x in range(bitsnum)], [pow(2,x) for x in range(bitsnum)]

        # keep 2 bytes to 0 in unit behavior
        payload = self.dev.request_cmd('unit_behavior')  
        time.sleep(1)        
        disablebit = int(payload[2:4], 16)
        disablebit_rawrate = int(payload[4:6], 16)              
        self.dev.set_cmd('set_unit_behavior', [0, 0, disablebit, disablebit_rawrate, self.dev.src])
        time.sleep(1) 

        for idx, value in enumerate(enable_list):
            # input('clear cantest dbc')
            self.dev.set_cmd('set_unit_behavior', [value, value, 0, 0, self.dev.src])  
            if bhr_set_ok == False:
                break          
            time.sleep(1)
            # input('123')
            payload = self.dev.request_cmd('unit_behavior')
            # input('123')
            if payload == False: 
                bhr_set_ok = False
            else:
                if self.debug: eval('print(k, i, j, m)', {'k':sys._getframe().f_code.co_name,'i':bhr_set_ok,'j':[idx, value, payload], 'm':['enable list:', enable_list]})
                if self.dev.decode_behavior_num(int(payload[2:4], 16))[idx] == 0:
                    bhr_set_ok = False
                if self.dev.decode_behavior_num(int(payload[4:], 16))[idx] == 0:
                    bhr_set_ok = False
            if self.debug or (bhr_set_ok == False): eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[idx, value, bhr_set_ok]}) 
        
        # keep 2 bytes to 255 in unit behavior.
        self.dev.set_cmd('set_unit_behavior', [255, 255, 0, 0, self.dev.src])
        time.sleep(1) 

        for idx, value in enumerate(disable_list):
            if bhr_set_ok == False:
                break
            self.dev.set_cmd('set_unit_behavior', [0, 0, value, value, self.dev.src])
            time.sleep(0.2)
            payload = self.dev.request_cmd('unit_behavior')
            if payload == False: 
                bhr_set_ok = False
            else:
                if self.dev.decode_behavior_num(int(payload[2:4], 16))[idx] == 1:
                    bhr_set_ok = False
                if self.dev.decode_behavior_num(int(payload[4:], 16))[idx] == 1:
                    bhr_set_ok = False
            if self.debug or (bhr_set_ok == False): eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':[idx, value, bhr_set_ok]}) 

        self.function_measure_data[sys._getframe().f_code.co_name] = bhr_set_ok      
        return bhr_set_ok

    def try_bank_ps0_list(self, target_data, algo_rst=0x60, hw_bit=0x62, sw_bit=0x63, status_bit=0x64, hr_acc=0x5C): # 5.9.1-5.9.5
        '''
        replaced by self.set_try_ps()
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        self.dev.set_to_default(pwr_rst = False)
        time.sleep(2)
        ps0_set_ok = True
        # algo_rst, hw_bit, sw_bit, status_bit, hr_acc = 0x60, 0x92, 0x93, 0x94, 0x5C
        data = [algo_rst, 0, hw_bit, sw_bit, status_bit, hr_acc, 0x00, 0x00]
        self.dev.set_cmd('set_bank_ps0', data)
        time.sleep(0.2)
        if algo_rst != 0x50:
            feedback = self.dev.set_get_feedback_payload(set_fb_name = 'algo_rst_feedback')
            feedback2 = self.dev.new_set_cmd(new_ps = algo_rst, data = [0, self.dev.src])
            if (feedback != False) or (feedback2 == False):
                ps0_set_ok = False
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':ps0_set_ok})
        if hw_bit != 0x52:            
            feedback3 = self.dev.request_cmd('hw_bit')
            feedback4 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + hw_bit)
            if (feedback3 != False) or (feedback4 == False):
                ps0_set_ok = False
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':ps0_set_ok})
        if sw_bit != 0x53:            
            feedback5 = self.dev.request_cmd('sw_bit')
            feedback6 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + sw_bit)
            if (feedback5 != False) or (feedback6 == False):
                ps0_set_ok = False
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':ps0_set_ok})
        if status_bit != 0x54:            
            feedback7 = self.dev.request_cmd('status')
            feedback8 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + status_bit)
            if (feedback7 != False) or (feedback8 == False):
                ps0_set_ok = False
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':ps0_set_ok})
        if hr_acc != 0x6C:
            feedback9 = self.get_msg(target_data='acc_hr',back_default=False)
            if self.debug: eval('print(k,m, i)', {'k':sys._getframe().f_code.co_name, 'm':'feedback9:','i':feedback9})
            feedback10 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + hr_acc)
            if (feedback9 != False) or (feedback10 == False):
                ps0_set_ok = False
            if self.debug: eval('print(k,i)', {'k':sys._getframe().f_code.co_name, 'i':ps0_set_ok})

        self.function_measure_data[sys._getframe().f_code.co_name] = ps0_set_ok
        self.dev.set_to_default()
        time.sleep(3)
        return ps0_set_ok

    def try_bank_ps1_list(self, target_data, pkt_rate = 0x75, pkt_type = 0x76, lpf_filter = 0x77, orientation = 0x78): # 5.9.6-5.9.9
        '''
        replaced by self.set_try_ps()
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        self.dev.set_to_default(pwr_rst = False)
        time.sleep(2)
        ps1_set_ok = True
        # pkt_rate = 0x55, pkt_type = 0x56, dig_filter = 0x57, orientation = 0x58
        if self.debug: eval('input([k, i])', {'k':sys._getframe().f_code.co_name, 'i':'before set bank ps1'})
        self.dev.empty_data_pkt()
        time.sleep(0.2)
        data = [pkt_rate, pkt_type, lpf_filter, orientation, 0x00, 0x00, 0x00, 0x00]
        self.dev.set_cmd('set_bank_ps1', data)
        time.sleep(0.2)
        if self.debug: eval('input([k, i])', {'k':sys._getframe().f_code.co_name, 'i':'after set bank ps1'})
        if pkt_rate != 0x55:            
            feedback3 = self.dev.request_cmd('pkt_rate')
            feedback4 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + pkt_rate)
            if (feedback3 != False) or (feedback4 == False):
                ps1_set_ok = False
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':[feedback3, feedback4, ps1_set_ok]})
        if pkt_type != 0x56:            
            feedback5 = self.dev.request_cmd('pkt_type')
            feedback6 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + pkt_type)
            if (feedback5 != False) or (feedback6 == False):
                ps1_set_ok = False
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':[feedback5, feedback6, ps1_set_ok]})
        if lpf_filter != 0x57:            
            feedback7 = self.dev.request_cmd('lpf_filter')
            feedback8 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + lpf_filter)
            if (feedback7 != False) or (feedback8 == False):
                ps1_set_ok = False
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':[feedback7, feedback8, ps1_set_ok]})
        if orientation != 0x58:
            feedback9 = self.dev.request_cmd('orientation')
            feedback10 = self.dev.new_request_cmd(src = 0, new_pgn = 0xFF00 + orientation)
            if (feedback9 != False) or (feedback10 == False):
                ps1_set_ok = False
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name, 'i':[feedback9, feedback10, ps1_set_ok]})
        self.function_measure_data[sys._getframe().f_code.co_name] = ps1_set_ok
        return ps1_set_ok

    def test_save_file(self, target_data): # 6
        '''
        if not find all zero in payload, True will feedback
        '''
        if self.debug: eval('print(k)', {'k':sys._getframe().f_code.co_name})
        self.dev.set_to_default(pwr_rst = False)
        time.sleep(0.2)
        self.dev.set_cmd('set_pkt_type', [pow(2, len(self.dev.predefine.get('types_name'))) - 1])
        time.sleep(0.2)
        self.dev.set_cmd('set_pkt_rate', [1])
        time.sleep(0.2)
        start_time = time.time()
        date_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_path = os.path.join(os.getcwd(), 'data',
                            'can_data_{0:#X}_{1:#X}_{2}_{3}.txt'.format(self.dev.src, self.dev.sn_can, self.dev.dev_type, date_time))
        f = open(file_path, 'w+', 1)
        print('start save data to file in 200s, pls wait, starting time:{0}, need wati 30s, pls wait!!'.format(date_time))
        all_zero = False
        while (time.time() - start_time) < 30: # recording 200s data
            for idx,item in enumerate(self.dev.auto_msg_queue):
                self.dev.auto_msg_queue_lock[idx].acquire()
                if item.empty():
                    self.dev.auto_msg_queue_lock[idx].release()      
                    time.sleep(0.001) 
                else:
                    msg_dict = item.get()
                    self.dev.auto_msg_queue_lock[idx].release() 
                    if int(msg_dict['payload'], 16) == 0:
                        all_zero = True 
                    f.write(str(msg_dict) + '\n')
            f.flush() # write to internal buffer, when full it will write to file by call()
            os.fsync(f) # force write to file now
        f.close()
        print('finished save data file: {0}'.format(file_path))
        self.function_measure_data[sys._getframe().f_code.co_name] = (all_zero == False)
        return all_zero == False





'''

    def try_unit_bhr_list_old(self, target_data):  # invalid now
        # check some behavior configuration items is set
        if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':target_data})
        enable_list       = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20]
        disable_list      = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20]
        bhr_set_ok        = True
        for value in enable_list:
            if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':'enabel_bit list'})
            if self.set_unit_behavior(target_data = hex(value)) == False:
                if self.debug: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':value})
                if self.debug: input('set behavior failed, pls press enter:')
                bhr_set_ok = False
        if bhr_set_ok == False:
            self.function_measure_data[sys._getframe().f_code.co_name] = bhr_set_ok 
            return bhr_set_ok
        for value in disable_list:
            print(bhr_set_ok)
            if self.debug: eval('print(k, i, set_ok)', {'k':sys._getframe().f_code.co_name,'i':'disable_bit list', 'set_ok':bhr_set_ok})
            if self.set_unit_behavior(target_data = '0x00', disable_bit = value) == False:
                bhr_set_ok = False   
        self.function_measure_data[sys._getframe().f_code.co_name] = bhr_set_ok      
        return bhr_set_ok

# feedback = self.save_confi_msg_queue.get()['payload']
# fb_type = int(feedback[:2], 16)
# fb_result = int(feedback[-2:], 16)                
# return True if fb_type == 1 and fb_result == 1 else False

# cmd_idx = feedback_des['fb_id']
# self.set_feedback_payload[cmd_idx] = None
# feedback_des = [x for x in self.can_attribute if x['type'] == 'feedback' and x['name'] == ''.join([cmd_name,'_feedback'])]



def with_sc_pwr_cycle(self, to_lpf_rate = 5, to_odr = 5, to_pkt_type = 0x0F, to_ori = 0x0009, to_behavior = 2):
    self.set_lpf_filter(to_lpf_rate)
    self.set_odr(to_odr)
    print('set pkt type')
    self.set_pkt_type(to_pkt_type)
    print('set ori')
    self.set_orientation(to_ori)
    self.set_unit_behavior(enabel_bit=0,disable_bit=1)
    self.save_configuration() # restart the unit
    if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
        self.dev.auto_power.power_off()
        time.sleep(4)
        self.dev.auto_power.power_on()
    else:
        while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
            pass
    time.sleep(2)
    # check the configurations saved or not
    print('check after power reset.')
    save_lpf_ok                 = True if self.get_lpf()[0] == to_lpf_rate else False
    save_odr_ok                 = True if self.get_packet_rate()[1] == to_odr else False
    save_pkt_type_ok            = True if self.get_packet_type() == to_pkt_type else False
    save_ori_ok                 = True if self.get_orientation() == to_ori else False
    save_behavior_ok            = True if self.get_unit_behavior() == to_behavior else False
    print('try to get again')
    print(self.get_packet_type())
    print('try finished.')
            
    return save_lpf_ok, save_odr_ok, save_pkt_type_ok, save_ori_ok, save_behavior_ok

def without_sc_pwr_cycle(self, to_lpf_rate = 5, to_odr = 5, to_pkt_type = 0x0F, to_ori = 0x0009, to_behavior = 2):
    self.set_lpf_filter(to_lpf_rate)
    self.set_odr(to_odr)
    self.set_pkt_type(to_pkt_type)
    self.set_orientation(to_ori)
    self.set_unit_behavior(enabel_bit=0,disable_bit=1)
    if self.dev.auto_power.enabled: # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off
        self.dev.auto_power.power_off()
        time.sleep(4)
        self.dev.auto_power.power_on()
    else:
        while input('need to reset power(!!!strong recommend let unit keep power off > 3s !!!), is it finished, y/n ? ') != 'y':
            pass
    time.sleep(2)
    self.driver.send_wakeup_msg() 

    # check the configurations saved or not
    back_lpf_ok                 = True if self.get_lpf()[0] == 25 else False
    back_odr_ok                 = True if self.get_packet_rate()[1] == 1 else False
    back_pkt_type_ok            = True if self.get_packet_type() == 7 else False
    back_ori_ok                 = True if self.get_orientation() == 0 else False
    back_behavior_ok            = True if self.get_unit_behavior() == 2 else False
            
    return back_lpf_ok, back_odr_ok, back_pkt_type_ok, back_ori_ok, back_behavior_ok

def try_bank_ps1_list(self):
    ps1_set_ok = False
    if self.set_bank_ps1(pkt_rate = 0x85, pkt_type = 0x86, dig_filter = 0x87, ori_request = 0x88) == True:
        ps1_set_ok = True
        print('ps1_set_ok',ps1_set_ok)
    else:
        print('try bank ps0 list, failed.')
    
    return ps1_set_ok

def try_bank_ps0_list(self):
    ps0_set_ok = False
    if self.set_bank_ps0(algo_rst=0x60, hw_bit=0x92, sw_bit=0x93, status_bit=0x94, acc_hr=0x95) == True:
        ps0_set_ok = True
        print('ps0_set_ok', ps0_set_ok)
    else:
        print('try bank ps0 list, failed.')
    
    return ps0_set_ok

def try_unit_bhr_list(self, actual_measure = False):
    # check some behavior configuration items is set
    enable_list       = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20]
    disable_list      = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20]

    bhr_set_ok        = True
    for value in enable_list:
        if self.set_unit_behavior(enabel_bit=value) == False:
            bhr_set_ok = False
            print('set unit behavior enale value:{0} failure, get_value status is:{1}:'.format(value, self.get_unit_behavior()))
    for value in disable_list:
        if self.set_unit_behavior(disable_bit=value) == False:
            bhr_set_ok = False
            print('set unit behavior disable value:{0} failure, get_value status is:{1}:'.format(value, self.get_unit_behavior()))
    
    return bhr_set_ok

def try_orientation_list(self):
    # check some orientation configuration items is valid
    origianl_orient            = self.get_orientation()
    ori_list          = [0x0000, 0x0009, 0x0023, 0x002A, 0x0041, 0x0048, 0x0062, 0x006B, 
                        0x0085, 0x008C, 0x0092, 0x009B, 0x00C4, 0x00CD, 0x00D3, 0x00DA, 0x0111, 
                        0x0118, 0x0124, 0x012D, 0x0150, 0x0159, 0x0165, 0x016C] 
    while input('Please place the unit horizontally to let program detect orientation configuraitons, is it horizontal placement, y/n ? ') != 'y':
        pass      
    ori_set_ok        = True
    for idx,value in enumerate(ori_list):
        if self.set_orientation(value) == False:
            ori_set_ok = False
        print(self.acceldata.get(), "--",self.acceldata.get()[-6:])
    self.set_orientation(origianl_orient)

    return ori_set_ok

def set_lpf_list(self):
    # check all lpf configuration list is valid
    original_rate, original_acc = self.get_lpf()
    lpf_list          = [0, 2, 5, 10, 20, 25, 40, 50] 
    lpf_set_ok        = True
    for value in lpf_list:
        if self.set_lpf_filter(value, value) == False:
            lpf_set_ok = False
            print('set lpf_rate and acc:{0} {1} failed'.format(value, value))
    self.set_lpf_filter(original_rate, original_acc)  
    return lpf_set_ok 

def try_pkt_type_list(self, actual_measure = False):
    # check all lpf configuration list is valid
    original_type = self.get_packet_type()
    type_list          = [0, 1, 2, 4, 3, 7, 8, 0xB, 0xF, 0xE, 0x13, 0x16, 0x17, 0x1B, 0x1C, 0x1E, 0x1F] 
    type_set_ok        = True
    for value in type_list:
        if self.set_pkt_type(value) == False:
            type_set_ok = False
            print('cannot set pkt_type value to: {0}'.format(value))
        if actual_measure == True:
            # pkt_rate = 100/value if value != 0 else 0
            # pass_delta    = 20 if value < 4 else 1
            pkt_type_mea = self.measure_pkt_type()
            if pkt_type_mea != value:
                type_set_ok = False   
                print('set packet type value:{0}, actual:{1}hz, seting invalid actually.'.format(value, pkt_type_mea))           
    self.set_pkt_type(original_type)  
    return type_set_ok 

def try_odr_list(self, actual_measure = False):
    # check all odr configuration list is valid by measure or not
    original_odr_idx      = self.get_packet_rate()[1]
    odr_list          = [0, 1, 2, 4, 5, 10, 20, 25, 50] # [0, 1, 2, 4, 5, 10, 20, 25, 50]
    odr_set_ok        = True
    for value in odr_list:
        if self.set_odr(value) == False:
            odr_set_ok = False
            print("can not change odr index to {0}".format(value))
        if actual_measure == True:
            pkt_rate = 100/value if value != 0 else 0
            pass_delta    = 20 if value < 4 else 1
            odr_mea = self.measure_odr()
            if abs(odr_mea - pkt_rate) > pass_delta:
                odr_set_ok = False   
                print('set odr:{0}hz, actual:{1}hz, seting invalid actually.'.format(pkt_rate, odr_mea))                 

    self.set_odr(original_odr_idx)
    return odr_set_ok

def measure_pkt_type(self):
    record_status = self.record
    if record_status == False:
        self.start_record()
    odr_idx = self.get_packet_rate()[1]
    self.set_odr(1)
    slope_exist, acc_exist, rate_exist, angle_ssi_exist, acc_hr_exist = 0, 0, 0, 0, 0
    if self.empty_data_pkt():            
        time.sleep(2) # wait 1s to receive packets again
        slope_exist       = 1 if self.slopedata.qsize() > 0 else 0
        rate_exist        = 2 if self.ratedate.qsize() > 0 else 0
        acc_exist         = 4 if self.acceldata.qsize() > 0 else 0
        angle_ssi_exist   = 8 if self.angle_ssi.qsize() > 0 else 0
        acc_hr_exist      = 16 if self.acc_hr.qsize() > 0 else 0  
    self.set_odr(odr_idx)
    if record_status == False:
        self.stop_record()      
    return sum([slope_exist, rate_exist, acc_exist, angle_ssi_exist, acc_hr_exist])

def measure_odr(self):
    
    # open the recording and set right packet type 
    # measure 5s, calc the received msg
    
    record_status = self.record
    if record_status == False:
        self.start_record()

    type_old = self.get_packet_type()
    self.set_pkt_type(7) 

    print("measuring ODR by SSI2 message in 5s, pls wait:")
    self.slopedata.queue.clear() 
    start_time = time.time()
    while time.time() - start_time < 5.0:
        time.sleep(0.2)
    odr = self.slopedata.qsize()/5 
    self.set_pkt_type(type_old)
    if record_status == False:
        self.stop_record()
    # print('finished, ODR is {0} hz'.format(odr))
    return odr  
'''