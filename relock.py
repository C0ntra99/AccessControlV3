import os
import time
import hardwareControl

os.chdir(os.path.dirname(os.path.abspath(__file__)))

file = 'unlock.lck'
door = hardwareControl.Door()
led = hardwareControl.Led()

while True:
    time.sleep(1)
    if os.path.exists(file) and (time.time() - os.path.getctime(file)) > (10):
        os.remove(file)
        door.lock()
        led.default(door)
