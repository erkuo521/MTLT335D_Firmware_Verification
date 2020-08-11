
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!")


class aceinna_gpio(): 
    '''
    for Raspberry cannot supply full power for 305D, so gpio pin can only suply 3.3v, i need another chip to control 5-32V power supply
    the chip can accept 0/3.3v input contrl, still under preparation.
    so self.enabled set to faulse firstly.
    '''
    def __init__(self, pwr_pin = 4, use_gpio = False):
        self.power_pin = pwr_pin # positve of power pin 
        self.gpio_setting()
        self.enabled = use_gpio # only if enabled, it will power on and off by gpio automaticaly.  default will not use auto-power, need manual power on and off

    def gpio_setting(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.power_pin,GPIO.OUT)
        GPIO.output(self.power_pin,GPIO.HIGH) # used as power positive line  in Pi3 board 


    def power_on(self):
        GPIO.output(self.power_pin,GPIO.HIGH) 
        print('power on now of pin_BCM: ', self.power_pin)

    def power_off(self):    
        GPIO.output(self.power_pin,GPIO.LOW) 
        print('power off now of pin_BCM: ', self.power_pin)
