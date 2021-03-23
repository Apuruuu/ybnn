import RPi.GPIO as GPIO
import dht11
import Adafruit_ADS1x15
import board
import busio

# import tkinter as tk
from time import strftime, localtime, sleep

from multiprocessing import Process, Pipe
# import GUI_by_tkinter

# import socket

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
I2C = busio.I2C(board.SCL, board.SDA)

def get_temp(pipe_sensor, pin=19):
    instance = dht11.DHT11(pin)
    while True:
        result = instance.read()
        if result.is_valid():
            pipe_sensor.send({'temperature':result.temperature, 'humidity':result.humidity})
            print(result.temperature,result.humidity)
        else:
            pipe_sensor.send({'temperature':"N/A", 'humidity':"N/A"})
            print('nodata')
        sleep(5)

def get_ADC_value(pipe_sensor):
    adc = Adafruit_ADS1x15.ADS1115(i2c=I2C)
    GAIN = 8

    while True:
        values = [0]*4
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN) * 0.512 / 2**15 

        # pipe_sensor.send({'turbidity':values[0], 'PH':values[1], 'ADC3_A2':values[2], 'ADC4_A3':values[3]})
        print('adc',values)
        sleep(1)
        
def get_time(pipe_sensor):
    while True:
        # pipe_sensor.send({'time':strftime("%Y-%m-%d %H:%M:%S", localtime())})
        sleep(1)

class Config(object):
    def __init__(self):
        pass

# class MainAPP(Config):
    # def __init__(self, pipe_sensor, pipe_main):
    #     if self.device_class = 'zhixin':
    #         self.UDP_sender()

    #     cache = {'temperature':'N/A', 
    #                     'humidity':'N/A',
    #                     'water_temperature':'N/A',
    #                     'PH':'N/A',
    #                     'lumen':'N/A',
    #                     'time':'N/A',
    #                     'turbidity':'N/A',
    #                     'height':'N/A',
    #                     }

    #     while True:
    #         data = pipe_sensor.recv()
    #         if isinstance(data,dict):
    #             cache = dict(cache, **data)
    #             if self.device_class = 'zhixin':
    #                 self.UDP_sender(cache)
    #         elif data == 'SHOW_ME_DATA':
    #             pipe_main.send(cache)
    #         else:
    #             continue

    # # UDP发送端
    # def UDP_sender(self,cache):
    #     buffersize=1024
    #     server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     server.bind(self.IP_address,self.port)

    # # UDP接收器
    # def UDP_(self):


        

class GPIO_CONT():
    def __init__(self,pipe_sensor,pipe_main):
        self.pipe_main = pipe_main
        while True:
            data = pipe_sensor.recv()
            if isinstance(data,tuple):
                _command = {'device':data[0], 'turn_to':data[1], 'timer':data[2], 'keep1':'', 'keep2':'', 'keep3':''}
            else:
                continue

            
        self.GPIO_PIN = {'light':21,'pump_1':20,'pump_2':16,'pump_air':None,'magnetic_stitter':None}

        self.devices = [['light','off','0','','',''],
                        ['pump_air','off','0','','',''],
                        ['pump_1','off','0','','',''],
                        ['pump2','off','0','','',''],
                        ['magnetic_stitter','off','0','','',''],
        ]

            

    def check_status(self):
        for i in range(len(self.devices)):
            if int(self.devices[i,2]) == 0 and self.devices[i,1] == 'off':
                continue

            if int(self.devices[i,2]) > 0 and self.devices[i,1] == 'off':
                self.devices[i,2] = int(self.devices[i,2]) - 1
                self.Turn_ON(self.GPIO_PIN[self.devices[i,0]])

            if int(self.devices[i,2]) == 0 and self.devices[i,1] == 'on':
                self.Turn_OFF(self.GPIO_PIN[self.devices[i,0]])

        self.pipe_main.send(self.devices)

    def Turn_ON(self,pin):
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.HIGH)

    def Turn_OFF(self,pin):
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.LOW)
        GPIO.cleanup(pin)    

if __name__ == '__main__':
    pipe_sensor = Pipe()
    pipe_main = Pipe()
    # mainapp = Process(target=MainAPP, args=(pipe_sensor[1], pipe_main[0]))
    temp = Process(target=get_temp, args=(pipe_sensor[0],))
    time = Process(target=get_time, args=(pipe_sensor[0],))
    adc = Process(target=get_ADC_value, args=(pipe_sensor[0],))
    # maingui = Process(target=GUI_by_tkinter.GUI, args=(pipe_sensor[0], pipe_main[1]))
    # gpio_cont = Process(target=GPIO_CONT, args=(pipe_sensor[1], pipe_main[0],))
    
    # mainapp.start()
    temp.start()
    time.start()
    adc.start()
    # maingui.start()
    # gpio_cont.start()

    # mainapp.join()
    temp.join()
    time.join()
    adc.join()
    # maingui.join()
    # gpio_cont.join()