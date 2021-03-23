import RPi.GPIO as GPIO
import time


def Get_depth(pin):

    # setup the pin as output
    GPIO.setup(pin, GPIO.OUT)

    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(pin, GPIO.LOW)
    start = time.time()

    # setup pin as input
    GPIO.setup(pin, GPIO.IN)

    # get duration from Ultrasonic SIG pin
    while GPIO.input(pin) == 0:
        continue
        
    stop = time.time()

    elapsed = stop-start
    distance = elapsed * 3430000 / 2

    print("Distance : %.1f MM" % distance)


if __name__ == '__main__':
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)
    pin = 26
    Get_depth(pin)