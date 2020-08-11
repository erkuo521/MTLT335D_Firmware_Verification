import serial
import time
import threading
from CRC16_class import CRC16

ping        = [0x50,0x4B,0x00]
ID          = [0x49,0x44]
VR          = [0x56, 0x52]

crc16 = CRC16()

###########################################################
class UART_Dev:
    ############## Private Methods ###############
    def __init__(self, port, baudrate):
        self.baudrate = baudrate
        self.port = port
        self.UUT = serial.Serial(port, baudrate, timeout = 2)
        self.header_bytes = 2
        self.packet_type_bytes = 2
        self.payload_len_bytes = 1
        self.crc_bytes = 2
        #self.thread_read = threading.Thread(target=self.read_msg)
        #self.thread_get = threading.Thread(target=self.get_msg)


    # appends Header and Calculates CRC on data
    # data should have packet_type + payload_len + payload
    def _create_packet(self, data):
        header = [0x55, 0x55]
        packet = []

        packet = packet + header
        packet = packet + data

        crc = crc16.crcb(data)
        crc_hex = hex(crc)[2:]

        # CRC has to be 4 char long + odd length strings dont go through bytearray.fromhex()
        if(len(crc_hex) < 4):
            for i in range(4-len(crc_hex)):
                crc_hex = "0"+crc_hex

        crc_bytes = bytearray.fromhex(crc_hex)
        packet.extend(crc_bytes)

        data = packet
        #print data
        # At this point, data is ready to send to the UUT
        return data

    # returns Packet_type, Payload_length, payload
    def _unpacked_response(self):
        str_list = self.read_response()
        packet_type = ""
        payload_length = ""
        payload = ""

        # when serial read times out, str_list is empty
        if not str_list:
            return packet_type, payload_length, payload
        # serial read was succesful
        else:
            packet_type = str_list[0]
            payload_length = str_list[1]
            payload = str_list[2]
            return packet_type, payload_length, payload

    # appends Header and Calculates CRC on data
    # data should have packet_type + payload_len + payload
    def _send_message(self, data):
        self.UUT.write(self._create_packet(data))

    ############## Public Methods ###############

    # Reads raw data from the UUT
    # Returns list of strings [Packet_type, Payload_length, payload]
    # Returns empty list in case of timeout
    def read_response(self, timeout = 10):
        retry = 0
        t0 = time.time()
        str_list = []
        while True:
            hex = self.UUT.read(1).encode("hex")
            if(len(hex) == 0):
                if(time.time() - t0 > timeout):
                    print "timed out"
                    return str_list

            elif(hex == '55'):
                hex = self.UUT.read(1).encode("hex")
                if(hex == '55'):
                    #once header found, read other fields from the packet
                    str_list.append(self.UUT.read(self.packet_type_bytes))
                    #print "Packet Type = " + packet_type
                    payload_size = self.UUT.read(self.payload_len_bytes).encode("hex")
                    str_list.append(payload_size)
                    str_list.append(self.UUT.read(int(payload_size,16)).encode("hex"))
                    #print "Data = " + data_hex
                    str_list.append(self.UUT.read(self.crc_bytes).encode("hex"))
                    #print "CRC = " + crc_hex
                    return str_list
            else:    # gets here if it received a byte that is not header(0x55)
                retry += 1
                t0 = time.time()
                if(retry > 100):
                    print "Error: Couldnt find header"
                    return str_list

    # Message type [2 bytes] = packet type
    # Message (N*4 bytes) = N * [field_id[2 bytes], field_val[2bytes]]
    #                          Message can have multiple field+val pairs
    # Enables user to just send field ID and Data
    # this methods automatically figures out number of fields and payload length
    # For the message types that dont need field address, send message directly
    def sensor_command(self, message_type, message):
        packet = []
        packet.extend(bytearray(message_type))

        # form packet to send
        if(message_type == "WF" or message_type == "SF"):
            msg_len = 1 + len(message)
            no_of_fields = len(message)/4
            packet.append(msg_len)
            packet.append(no_of_fields)
            final_packet = packet + message
            #print packet
        elif(message_type == "GF" or message_type == "RF"):
            msg_len = 1 + len(message)
            no_of_fields = len(message)/2
            packet.append(msg_len)
            packet.append(no_of_fields)
            final_packet = packet + message
        else:
            msg_len = len(message)
            packet.append(msg_len)
            final_packet = packet + message
            #print final_packet

        # Retrive any unread bytes in buffer
        nbytes = self.UUT.inWaiting()
        if nbytes > 0:
            indata = self.UUT.read(nbytes)
        #rint final_packet
        # Write command to sensor
        self.UUT.write(self._create_packet(final_packet))

        # Read Response
        response = self.read_response()

        if response:
            if(response[0] == message_type):
                #print response[0], response[2]
                return response[2]          # just payload
            elif("GP" == message_type):
                return response             # packet_type + payload_len + payload
            else:
                #print "resp", response
                return response
        else:
            print "Error: No response Received in sensor_commnd"
            return None

        ''' TODO
        def get_command(field, field_val):
        def set_command(field, field_val):
        def read_command(field, field_val):
        def write_command(field, field_val):
        '''
    ############## Direct Commands ###############
    # set packet rate = Quiet
    def silence_device(self):
        retry = 0
        self._send_message([0x53,0x46,0x05,0x01,0x00,0x01,0x00,0x00])
        response = self.read_response()
        #print "silence dev resp:", response
        time.sleep(2)
        # Retrive any unread bytes in buffer
        nbytes = self.UUT.inWaiting()
        if nbytes > 0:
            indata = self.UUT.read(nbytes)


    # returns true if ping was successful
    def ping_device(self):
        self._send_message(ping)
        pt,pll,pl = self._unpacked_response()
        if(pt == "PK"):
            return True
        else:
            return False

    def restart_device(self):
        self._send_message([0x53,0x52,0x00])
        response = self.read_response()
        while(response[0] != "SR"):
            response = self.read_response()
        time.sleep(2)# Allow unit to back up

    def get_serial_number(self):
        response = self.sensor_command("GP", ID)

        while(response[0] != "ID"):
            response = self.read_response()

        serial_number = response[2][:8]
        model_string = response[2][8:]

        return int(serial_number,16), model_string.decode("hex")

    def get_version(self):
        response = self.sensor_command("GP", VR)

        while(response[0] != "VR"):
            response = self.read_response()

        major = int(response[2][0],16)
        minor = int(response[2][1],16)
        patch = int(response[2][2],16)
        stage = int(response[2][3],16)
        build = int(response[2][4],16)
        return str(major)+"."+str(minor)+"."+str(patch)+"."+str(stage)+"."+str(build)
