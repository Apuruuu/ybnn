import RPi.GPIO as GPIO
import dht11

import tkinter
import time
import datetime

from multiprocessing import Process, Pipe
import time
from unit.Temp import Tsensor

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)


def get_temp(pipe, pin=19):
    instance = dht11.DHT11(pin)
    while True:
        result = instance.read()
        if result.is_valid():
            pipe.send({'temperature' = result.temperature, 'humidity' = result.humidity})
        else:
            pipe.send({'temperature' = "N/A", 'humidity' = "N/A"})
        time.sleep(1)

def get_time(pip):
    pipe.send({'time' = time.asctime})
    time.sleep(1)

def MainAPP(pipe):
    cache = {}
    while True:
        data = pipe.recv()
        cache = dict(cache, **data)
        # print(cache)  #{'time': 'Sun Nov 29 16:54:28 2020', 'temp': 2}




if __name__ == '__main__':
    pipe = Pipe()
    mainapp = Process(target=MainAPP, args=(pipe[1],))
    temp = Process(target=get_temp, args=(pipe[0],))
    time = Process(target=get_time, args=(pipe[0],))

    mainapp.start()
    temp.start()
    time.start()

    mainapp.join()
    temp.join()
    time.join()