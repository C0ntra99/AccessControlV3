import configparser
import os
from threading import Thread
import RPi.GPIO as GPIO
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

##Read config file for GPIO pins
config = configparser.ConfigParser()
config.read('config.ini')

##Set up GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

class Led:

    GREEN = int(config['LEDs']['green'])
    AMBER = int(config['LEDs']['amber'])
    RED = int(config['LEDs']['red'])


    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(AMBER, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)

    def turnOn(self, color):
        ##Turn on color
        GPIO.output(color, True)

    def turnOff(self, color):
        GPIO.output(color, False)

    def flashColor(self, color):
        for x in range(3):
            GPIO.output(color, True)
            time.sleep(.3)
            GPIO.output(color, False)

    def default(self, door):
        if not door.is_blocked():
            GPIO.output(self.RED, False)
            GPIO.output(self.GREEN, False)
            GPIO.output(self.AMBER, True)
        else:
            GPIO.output(self.RED, True)
            GPIO.output(self.GREEN, False)
            GPIO.output(self.AMBER, False)

    def flash(self, times):
        for x in range(times):
            ##Turn on
            GPIO.output(self.RED, True)
            GPIO.output(self.GREEN, True)
            GPIO.output(self.AMBER, True)
            time.sleep(.3)
            ##Turn off
            GPIO.output(self.RED, False)
            GPIO.output(self.GREEN, False)
            GPIO.output(self.AMBER, False)

class Beeper:

    pin = int(config['Beeper']['beeper'])

    GPIO.setup(pin, GPIO.OUT)
    GPIO.setup(pin, False)
    def beep(self, num, tim):
        ##Beep 3 times for 3 seconds
        for x in range(num):
            GPIO.PWM(self.pin, 10)
            GPIO.output(self.pin, True)
            time.sleep(tim)
            GPIO.output(self.pin, False)
            time.sleep(tim)


class Door:

    pin = int(config['Door']['control'])
    led = Led()
    beeper = Beeper()

    GPIO.setup(pin, GPIO.OUT)
    GPIO.setup(pin, False)

    def unlock(self):
        ##Open door
        if not os.path.exists('block.lck'):
            if not os.path.exists('unlock.lck'):
                open('unlock.lck', 'w')
            #print("Open Door")
            GPIO.output(self.pin, True)
            self.led.turnOff(Led.AMBER)
            self.led.turnOn(Led.GREEN)
            GPIO.output(self.pin, True)
            return True
        else:
            ##Log the door is unlocked
            return False

    def lock(self):
        ##close door
        if os.path.exists('unlock.lck'):
            os.remove('unlock.lck')
        GPIO.output(self.pin, False)
        self.led.default(self)

    def block(self):
        ##Not allow open to work until unlocked
        self.led.turnOff(Led.AMBER)
        self.led.turnOn(Led.RED)
        if not os.path.exists('block.lck'):
            open('block.lck', 'w')

    def unblock(self):
        self.led.turnOff(Led.RED)
        self.led.turnOn(Led.AMBER)
        if os.path.exists('block.lck'):
            os.remove('block.lck')
        self.led.default(self)
    
    def is_open(self):
        return False

    def is_blocked(self):
        if os.path.exists('block.lck'):
            return True
        else:
            return False
        ##Unlock to lock

    def is_locked(self):
        if os.path.exists('unlock.lck'):
            return False
        else:
            return True
        ##Unlock to lock
