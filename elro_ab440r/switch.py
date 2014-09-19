#!/usr/bin/env python
"""
Switching ELRO plugs using the Raspberry Pi.
Jeroen Seegers 2014

Based on the work of djjaz (http://www.raspberrypi.org/forums/viewtopic.php?f=32&t=32177)
"""
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print "Error importing RPi.GPIO"

import time

class ElroSwitch(object):
    repeat = 10
    pulselength = 300

    def __init__(self, unit, code, pin):
        self.unit = unit
        self.code = code
        self.pin = pin
        self.charlist = [
            142, 142, 142, 142, 142,    # Dipswitch code
            142, 142, 142, 142, 142,    # Unit code
            142, 136,                   # On / off code (default: On)
            128, 0, 0, 0
        ]      
        self.bitlist = []

        self._set_system_code()
        self._set_unit_code()

    def switchOn(self):
        self._switch(GPIO.HIGH)

    def switchOff(self):
        self._switch(GPIO.LOW)

    def _switch(self, switch):
        if switch == GPIO.HIGH:
            self.charlist[10] = 136
            self.charlist[11] = 142

        self._to_binary(self.charlist)

        GPIO.output(self.pin, GPIO.LOW)
        for z in range(self.repeat):
            for bit in self.bitlist:
                GPIO.output(self.pin, bit)
                time.sleep(self.pulselength/1000000.)

    def _to_binary(self, bits):
        """
        Convert every int in input list to 8 digit binary list
        """
        for y in range(len(bits)):
            bitstring = "{0:08b}".format(bits[y])
            [self.bitlist.append(int(x)) for x in bitstring]

    def _set_system_code(self):
        for i in range(5):
            if self.code[i] == 1:
                self.charlist[i] = 136

    def _set_unit_code(self):
        x=1
        for i in range(1,6):
            if (self.unit & x) > 0:
                self.charlist[4+i] = 136
            x = x<<1

if __name__ == '__main__':
    import sys
    import config

    # Set the mode which we want to use for the GPIO communication.
    # GPIO.BOARD uses the physical pin numbers (which is the same between different board revisions).
    # GPIO.BCM uses the Broadcom SOC channel numbers (which changed between different board revisions).
    # For an overview of the different channels/pins, check the /docs folder in the repository.
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(config.PIN_OUT, GPIO.OUT)

    if len(sys.argv) < 3:
        print "Usage: python {filename} int_unit int_state".format(filename=sys.argv[0])
        sys.exit(1)

    device = ElroSwitch(
        unit=int(sys.argv[1]),
        code=config.DIPSWITCH_CODE,
        pin=config.PIN_OUT
    )

    if int(sys.argv[2]) == 1:
        device.switchOn()
    else:
        device.switchOff()

    GPIO.cleanup()
