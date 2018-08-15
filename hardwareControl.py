import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini')

class Door:
    def __init__(self):
        pin: int  = config['Door']['control']

    def open(self):
        ##Open door
        if not os.path.exists('lock.lck'):
            print("Open Door")
            #GPIO.output(self.pin, True)
            return True
        else:
            ##Log the door is unlocked
            raise

    def close(self):
        ##close door
        GPIO.output(self.pin, False)
    def lock(self):
        ##Not allow open to work until unlocked
        if not os.path.exists('lock.lck'):
            open('lock.lck', 'w')

    def unlock(self):
        if os.path.exists('lock.lck'):
            os.remove('lock.lck')
        ##Unlock to lock

class Led:
    def __init__(self):
    ##Setup GPIO pins
        GREEN: int = config['LEDs']['green']
        RED: int = config['LEDs']['red']
        BLUE: int = config['LEDs']['blue']

    def turnOn(self, color):
        ##Turn on color
        GPIO.output(color, True)

    def flash(self, times):
        for x in range(times):
            ##Turn on
            GPIO.output(self.RED, True)
            GPIO.output(self.GREEN, True)
            GPIO.output(self.BLUE, True)
            time.sleep(.3)
            ##Turn off
            GPIO.output(self.RED, False)
            GPIO.output(self.GREEN, False)
            GPIO.output(self.BLUE, False)

class Beeper:
    def __init__(self):
        pin: int = config['Beeper']['beeper']

    def beep(self, length=.3, num=3):
        ##Beep 3 times for 3 seconds
        for x in range(num):
            GPIO.output(self.pin, True)
            time.sleep(length)
            GPIO.output(self.pin, False)
