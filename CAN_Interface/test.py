import os
import time
# import xlwings as xw
from excel_sheet import my_csv
from communicator import aceinna_uart

# uart = aceinna_uart("/dev/ttyUSB0", 57600) 
# get_value = []
# while len(get_value) == 0:
#     uart.send_msg(data=[0x55, 0x55, 0x52, 0x46, 0x03, 0x01, 0x00, 0x3a, 0x2d, 0xf2])  
#     get_value = uart.get_msg()
#     time.sleep(0.5)    

# print(get_value) 




test_80 = my_csv(os.path.join(os.getcwd(), 'data', 'result.csv'))
test_80.write([[99, 88, 77], [99, 88, 77], [99, 88, 77]])

print(1)

del test_80
pass