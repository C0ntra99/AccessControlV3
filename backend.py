##Try excepts, log the error
##Handle the backend
from hardwareControl import Door, Led, Beeper
from databases.database import Database
from threading import Thread
from databases.tableDef import *
import datetime
import sys
import time
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def log(user, event, time):
    log = AccessLog(user, event, time)
    userDB.add(log)

def checkCard(card):
    ##Query database
    q = userDB.query(card)
    if len(q) > 0:
        log(q[0].name, "Allowed",datetime.datetime.now())
        return True
    else:
        user = User(id = card)
        log(user.id, "Denied", datetime.datetime.now())
        return False

def main():
    while True:
        led.default(door)
        rawCard = input("SwipeCard: ")
        formCard = rawCard[1:8]; print(door.is_blocked())

        if door.is_blocked():
            continue

        if checkCard(formCard):
            if door.unlock():
                print("Door open")
                Thread(target=beeper.beep, args=(5,.05)).start()
                time.sleep(3)
            else:
                print("Door is locked: ")

            door.lock()
        else:
            #Flash LEDs
            Thread(target=beeper.beep, args=(1,1)).start()
            led.flashColor(Led.RED)


if __name__ == "__main__":
        userDB = Database()
        door = Door()
        led = Led()
        beeper = Beeper()
        main()
