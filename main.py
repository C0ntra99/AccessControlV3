##Try excepts, log the error
##Handle the backend
from hardwareControl import Door, Led, Beeper
import database
from threading import Thread

def log(message):
    print("Log:", message)

def checkCard(card):
    ##Query database
    if card == "123":
        return True
    else:
        return False

def main():
    door = Door()
    led = Led()
    beeper = Beeper()
    door.unlock()
    while True:
        rawCard = input("SwipeCard: ")
        formCard = rawCard[1:8]
        if checkCard(formCard):
            door.open()
            Thread(target=beeper.beep()).start()
            time.sleep(3)
            door.close()
            log("{}:{}:{}".format(formCard, "Allowed", "DATE"))
        else:
            log("{}:{}:{}".format(formCard, "Denied", "DATE"))

    try:
        door.open()
        print("Door open")
    except:
        print("Door is locked")

main()
