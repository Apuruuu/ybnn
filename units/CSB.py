import RPi.GPIO as GPIO
from time import time, sleep

def Get_depth(pin):
    GPIO.setup(pin, GPIO.OUT)

    GPIO.output(pin, GPIO.LOW)
    sleep(0.2)
    GPIO.output(pin, GPIO.HIGH)
    sleep(0.5)
    GPIO.output(pin, GPIO.LOW)
    start = time()

    # setup pin as input
    GPIO.setup(pin, GPIO.IN)

    # get duration from Ultrasonic SIG pin
    while GPIO.input(pin) == 0:
        start = time()

    while GPIO.input(pin) == 1:
        end = time()

    # Calculate pulse length
    time_difference = end-start
    depth = (time_difference * 340000) / 2

    return depth

if __name__ == '__main__':
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)
    pin = 26
    depth = Get_depth(pin)
    print("Distance : %.1f mm" % depth)