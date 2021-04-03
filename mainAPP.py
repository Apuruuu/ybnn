import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Pipe

import os
import socket
import configparser
from Load_config import Config

# 初始化GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

def get_temp(pipe_sensor):
    import units.dht11

    pin=int(Config().conf.get('GPIO_PIN','DHT11'))
    instance = units.dht11.DHT11(pin)
    Wait_time = float(Config().conf.get('DHT11','WAIT_TIME'))

    while True:
        result = instance.read()
        if result.is_valid():
            pipe_sensor.send({'server_time':get_time(),
                                'temperature':result.temperature,
                                'humidity':result.humidity})
            print(result.temperature,result.humidity)
        else:
            continue
        time.sleep(Wait_time)

def get_ADC_value(pipe_sensor):
    import units.ADS1x15

    adc = units.ADS1x15.ADS1115()
    GAIN = Config().conf.getint('ADC','GAIN')
    Wait_time = float(Config().conf.get('ADC','WAIT_TIME'))

    while True:
        # 读取ADC所有信道的值
        values = [0]*4
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN)
        print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
        pipe_sensor.send({'server_time':get_time(),
                        'PH':values[0],
                        'turbidity':values[1],
                        'ADC3_A2':values[2],
                        'ADC4_A3':values[3]})
        time.sleep(Wait_time)

def get_height(pipe_sensor):
    import units.Ultrasonic_ranger

    pin = int(Config().conf.get('GPIO_PIN','UR'))
    Wait_time = float(Config().conf.get('UR','WAIT_TIME'))

    while True:
        height = units.Ultrasonic_ranger.Get_depth(pin)
        pipe_sensor.send({'server_time':get_time(),
                            'height':height})
        time.sleep(Wait_time)

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def send_time(pipe_sensor):
    pipe_sensor.send({'server_time':get_time()})

class MainAPP(Config):
    def __init__(self, pipe_sensor, pipe_UDP):
        self.status = {'server_time':'N/A',
                'temperature':'N/A', 
                'humidity':'N/A',
                'water_temperature':'N/A',
                'PH':'N/A',
                'lumen':'N/A',
                'turbidity':'N/A',
                'height':'N/A',
                'light':0,
                'pump_air':0,
                'pump_1':0,
                'pump2':0,
                'magnetic_stitter':0,
                }

        cache_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_CACHE_PATH')),
                                        str(time.strftime("%Y_%m_%d_%H_%M_%S.txt", time.localtime())))
        with open(cache_file_path, 'a') as cache_file:
            while True:
                data = pipe_sensor.recv()
                print(data)
                if isinstance(data,dict):
                    # 写入文件
                    cache_file.write(str(data))
                    cache_file.write('\n')
                    self.status = dict(self.status, **data)
                elif data == "send_to_UDP_server":
                    pipe_UDP.send(self.status)
                else:
                    continue

class UDP_server(Config):
    def __init__(self, pipe_sensor, pipe_UDP):
        self.Get_local_IP()
        print("Localhost_IP = ",self.Localhost)
        self.port = int(Config().conf.get('UDP server','PORT'))
        self.server(pipe_sensor, pipe_UDP)
        self.UDP_log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_CACHE_PATH')),
                                            str(Config().conf.get('Defult setting','UDP_log_file')),
                                            str(time.strftime("%Y_%m_%d_%H_%M_%S.txt", time.localtime()))                                    )

    def Get_local_IP(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            self.Localhost = s.getsockname()[0]
            Config().write('UDP server','LOCALHOST',self.Localhost)
            print('Localhost =', self.Localhost,":",Config().conf.get('UDP server','PORT'))

        finally:
            s.close()

    def log(self, ip, port):
        log = 0
        with open(self.UDP_log_file_path, 'w') as udp_log:
            udp_log.write(str(log))

    def server(self, pipe_sensor, pipe_UDP):
        server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server.bind((self.Localhost, self.port)) #绑定服务器的ip和端口
        while True:
            data, client_addr=server.recvfrom(1024) #一次接收1024字节
            data = data.decode(encoding='utf-8').upper()
            print(data,'from',client_addr)# decode()解码收到的字节
            print(type(data))
            data = eval(data)
            # # log
            if data['COMMAND'] == 0:
                print("获取数据")
                message = "send_to_UDP_server"
                pipe_sensor.send(str(message))
                print("s1")
                return_data = pipe_UDP.recv()
                print("s2")
                server.sendto(str(return_data).encode(encoding='utf-8'),client_addr)
                print(return_data,"send to",client_addr)
            else:
                continue

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
    cache_dir = os.path.join(str(Config().conf.get('Defult setting','DEFULT_CACHE_PATH')))
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    pipe_sensor = Pipe()
    pipe_GPIO = Pipe()
    pipe_UDP = Pipe()

    mainapp = Process(target=MainAPP, args=(pipe_sensor[1],pipe_UDP[0]))
    temp = Process(target=get_temp, args=(pipe_sensor[0],))
    height = Process(target=get_height, args=(pipe_sensor[0],))
    adc = Process(target=get_ADC_value, args=(pipe_sensor[0],))
    udp_server = Process(target=UDP_server, args=(pipe_sensor[0],pipe_UDP[1]))
    gpio_cont = Process(target=GPIO_CONT, args=(pipe_sensor[0],pipe_GPIO[1]))

    mainapp.start()
    temp.start()
    height.start()
    adc.start()
    udp_server.start()
    gpio_cont.start()

    mainapp.join()
    temp.join()
    height.join()
    adc.join()
    udp_server.join()
    gpio_cont.join()

# 结束子进程？
    # p.process.signal(signal.SIGINT)