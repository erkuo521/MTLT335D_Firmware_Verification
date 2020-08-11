import threading
import serial
from MTLT305_Uart import UART_Dev

class Messaging:

    def __init__(self, port, baudrate):
        self.mtlt305 = UART_Dev(port, baudrate)
        self.receive_thread = threading.Thread(target = receive_messages, args=(1,), daemon=True)
        self.send_thread = threading.Thread(target = receive_messages, args=(1,), daemon=True)
        self.receive_thread = start()

    def receive_messages(self):
        while True:
            self.mtlt305.

    def send_messages(self):
