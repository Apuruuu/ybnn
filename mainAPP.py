import RPi.GPIO as GPIO
import dht11
import Adafruit_ADS1x15

import tkinter as tk
import time
from time import strftime

from multiprocessing import Process, Pipe
import GUI_by_tkinter

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

def get_temp(pipe_sensor, pin=19):
    instance = dht11.DHT11(pin)
    while True:
        result = instance.read()
        if result.is_valid():
            pipe.send({'temperature':result.temperature, 'humidity':result.humidity})
        else:
            pipe.send({'temperature':"N/A", 'humidity':"N/A"})
        time.sleep(1)

def get_ADC_value(pipe_sensor):
    adc = Adafruit_ADS1x15.ADS1115()
    GAIN = 8

    while True:
        values = [0]*4
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN) * 0.512 / 2**15 

        pipe.send({'turbidity':values[0], 'PH':values[1], 'ADC3_A2':values[2], 'ADC4_A3':values[3]})
        time.sleep(1)
        
def get_time(pipe_sensor):
    while True:
        pipe_sensor.send({'time':strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        time.sleep(1)

class Config(object):
    def __init__(self):
        print('0')

class MainAPP(Config):
    def __init__(self, pipe_sensor, pipe_main):

        self.cache = {'temperature':'N/A', 
                        'humidity':'N/A',
                        'water_temperature':'N/A',
                        'PH':'N/A',
                        'lumen':'N/A',
                        'time':'N/A',
                        'turbidity':'N/A',
                        'height':'N/A',
                        }
        while True:
            data = pipe_sensor.recv()
            if isinstance(data,dict):
                self.cache = dict(self.cache, **data)
            elif data == 'SHOW_ME_DATA':
                pipe_main.send(self.cache)
            else:
                continue

    def value(self):
        return self.cache

class MainGUI(MainAPP):
    def __init__(self, pipe_sensor, pipe_main):
        GUI_by_tkinter.GUI(pipe_sensor, pipe_main)

if __name__ == '__main__':
    pipe_sensor = Pipe()
    pipe_main = Pipe()
    mainapp = Process(target=MainAPP, args=(pipe_sensor[1], pipe_main[0]))
    temp = Process(target=get_temp, args=(pipe_sensor[0],))
    time = Process(target=get_time, args=(pipe_sensor[0],))
    maingui = Process(target=MainGUI, args=(pipe_sensor[0], pipe_main[1]))

    mainapp.start()
    temp.start()
    time.start()
    maingui.start()

    mainapp.join()
    temp.join()
    time.join()
    maingui.join()