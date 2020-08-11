'''
CAN testing script
v1.0.0 20200509
'''

import os
import sys
import time
import json
from excel_sheet import my_csv
from device import aceinna_device
from driver import aceinna_driver
from test_case import aceinna_test_case
from gpio import aceinna_gpio

# def main(debug_main = False, dev_type = 'MTLT305D'):
def main(dev_type = 'MTLT305D', bcm_pin_list = []): 
    start_time = time.time()   
    with open('can_attribute_' + dev_type + '.json') as json_data:
        can_attribute = json.load(json_data)
    debug_main = True if can_attribute['debug_mode'].upper() == 'TRUE' else False
    testitems = can_attribute['test_items'] # testitems = ['3.6']

    gpio_list = []
    bcm_pin_list.sort()
    for pin in bcm_pin_list: # created gpio instance based on pins, sorted the list firstly
        exec(f'gpio_{pin}=aceinna_gpio(pwr_pin = {pin})') # sequence is correspond to sequency indev_nodes.
        exec(f'gpio_list.append(gpio_{pin})')  

    main_driver = aceinna_driver(debug_mode = debug_main)
    dev_nodes = main_driver.get_can_nodes()    

    device_list = []
    for idx,i in enumerate(dev_nodes):
        ad = aceinna_device(i, attribute_json = can_attribute,debug_mode = debug_main, power_gpio=gpio_list[idx])
        main_driver.register_dev(dev_src = i, instance_dev = ad) # regist each device to driver
        ad.add_driver(main_driver)
        ad.update_sn()
        device_list.append(ad) # add each device instance to device_list
    if debug_main: eval('print(k, i)', {'k':sys._getframe().f_code.co_name,'i':len(device_list)})

    for i in device_list:
        print('start testing device_src:{0} device_sn:{1}'.format(hex(i.src), hex(i.sn_can)))
        if debug_main: eval('input([k, i, j, m])', {'k':sys._getframe().f_code.co_name,'i':hex(i.sn_can), 'j':hex(i.src), 'm':'press enter:'})
        test_file = my_csv(os.path.join(os.getcwd(), 'data','result_{0:#X}_{1:#X}_{2}_FW{3}.csv'.format(i.src, i.sn_can, dev_type, can_attribute['predefine']['fwnum'])))
        main_test = aceinna_test_case(test_file, debug_mode = debug_main)
        main_test.set_test_dev(i, fwnum=int(can_attribute['predefine']['fwnum'], 16))  # need to be updated for each testing ----------input: 1        
        main_test.run_test_case(test_item = testitems, start_idx = can_attribute['start_idx']) # do single/multi items test in testitems list if needed
    print(f'testing finished, {time.time()-start_time} seconds used')
    
    return True

if __name__ == "__main__":
    input('will start main(), press Enter:')
    try:
        print(time.time())
        # main(debug_main = False, dev_type = 'OPEN335RI')  # open debug mode
        main(dev_type = 'MTLT305D', bcm_pin_list=[4])  # from type in JSON
    except Exception as e:
        print(e)
  
    