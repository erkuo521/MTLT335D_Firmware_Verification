# MTLT335_Firmware_Verification_Scripts

## CAN INTERFACE
MTLT335 - CAN Interface Verification Scripts

### Requirements
<TODO:>
### How to run the Script
<TODO:>

## UART INTERFACE
MTLT335 - UART Interface Verification Scripts

### Requirements
1. IMU connected to HOST PC through USB-RS232 Interface
2. Serial Port Name

### How to run the Script
Update serial port name and baudrate in MTLT335_Verification.py on line 19

>eg: uut = UART_Dev("/dev/tty.usbserial-142400", 115200 )
> uut = UART_Dev("/dev/tty.usbserial-144400", 57600 )


### To add more tests
Verification Scripts follow following test hierarchy. To add new tests, create a test_section and add test_cases. Each test case will require a handler function that has testing implementation. This implementation method will be part of Test_Scripts class. Use test implementation method name as a parameter in test_case. All methods in Test_Scripts class should return a list in this format only --> [Bool, Actual Result, Expected Result]

### Test Hierarchy
```
    <test_section>
      <test_cases> </test_cases>

      <test_cases> </test_cases>

                  .
                  .
      <test_cases> </test_cases>
    </test_section>
```
## To add more test cases
MTLT335_Tests.py file contains all the test cases and their implementation. *test_environment* class
registers test cases and test sections. This class is responsible for running all the registered test cases and storing the results. Implementation of each test case is inside *test_script* class.
