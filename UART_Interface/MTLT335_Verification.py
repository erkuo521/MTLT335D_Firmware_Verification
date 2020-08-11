from MTLT335_Uart import UART_Dev
from Test_Cases import Test_Section
from Test_Cases import Test_Case
from MTLT335_Tests import Test_Scripts
from MTLT335_Tests import Test_Environment
#import scripts

def ping_message_test():
    print " "

def unit_baudrate_test():
    print "printing from function"

def continuous_packet_type_test():
    print "printing from function"

if __name__ == "__main__":

    uut = UART_Dev("/dev/tty.usbserial-FTH1RYN0", 115200 )
    print("\r\n \t#######   MTLT335D UART Interface Verification V1.1   #######\r\n")
    serial_number, model = uut.get_serial_number()
    version = uut.get_version()

    print "\r\n \t# UUT Model: ", model
    print "\r\n \t# UUT Serial Number: ", serial_number
    print "\r\n \t# UUT Version: ", version

    print "\r\n \t##########  Setting up tests...  ##########################\r\n"
    uut.silence_device()

    env = Test_Environment(uut)
    env.setup_tests()
    print "\r\n \t##########  Executing tests...   ##########################\r\n"
    env.run_tests()
    print "\r\n \t##########  Results   #####################################\r\n"
    env.print_results()

    file_name = 'test_results_' + str(serial_number) + '_' + str(version) + '.csv'
    env.log_results(file_name)
