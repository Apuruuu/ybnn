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

    pin=int(Config().conf.get('SENSOR PIN','DHT11'))
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

    pin = int(Config().conf.get('SENSOR PIN','UR'))
    Wait_time = float(Config().conf.get('UR','WAIT_TIME'))

    while True:
        height = units.Ultrasonic_ranger.Get_depth(pin)
        pipe_sensor.send({'server_time':get_time(),
                            'height':height})
        time.sleep(Wait_time)

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

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

        log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_LOG_PATH')),
                                        str(time.strftime("%Y_%m_%d_%H_%M_%S.txt", time.localtime())))
        with open(log_file_path, 'a') as log_file:
            while True:
                data = pipe_sensor.recv()
                print(data)
                if isinstance(data,dict):
                    # 写入文件
                    log_filee.write(str(data))
                    log_file.write('\n')
                    self.status = dict(self.status, **data)
                elif data == "send_to_UDP_server":
                    pipe_UDP.send(self.status)
                elif data == "GPIO":
                    pipe_GPIO.send(self.status)
                else:
                    continue

class UDP_server(Config):
    def __init__(self, pipe_sensor, pipe_UDP, pipe_GPIO):
        self.Get_local_IP()
        print("Localhost_IP = ",self.Localhost)
        self.port = int(Config().conf.get('UDP server','PORT'))
        self.server(pipe_sensor, pipe_UDP)
        self.UDP_log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_LOG_PATH')),
                                            str(Config().conf.get('Defult setting','UDP_log_file_path')),
                                            str(time.strftime("%Y_%m_%d_%H_%M_%S.txt", time.localtime())))

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
        with open(self.UDP_log_file_path, 'a') as udp_log:
            udp_log.write(str(log))
            udp_log.write("\n")

    def server(self, pipe_sensor, pipe_UDP, pipe_GPIO):
        server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server.bind((self.Localhost, self.port)) #绑定服务器的ip和端口
        print("UDP server",self.Localhost,"liscening",self.port)
        while True:
            data, client_addr=server.recvfrom(1024) #一次接收1024字节
            data = data.decode(encoding='utf-8').upper()
            print(data,'from',client_addr)# decode()解码收到的字节
            data = eval(data)
            # # log
            if data['COMMAND'] == 'GET_DATA': # 获取数据
                message = "send_to_UDP_server"
                pipe_sensor.send(str(message))
                return_data = pipe_UDP.recv()
                server.sendto(str(return_data).encode(encoding='utf-8'),client_addr)
                print(return_data,"send to",client_addr)
            elif data['COMMAND'] == 1: # 硬件操作
                pipe_sensor.send({data['DEVICE_NAME'],data['ON_TIME']})

            else:
                continue

class GPIO_CONT():
    def __init__(self,pipe_sensor,pipe_GPIO):
        

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

class sys_timer(Config):
    def __init__(self, pipe_sensor, pipe_GPIO):
        pipe_sensor.send(str("GPIO"))
        status = pipe_GPIO.recv()
        self.time_start = time.time()
        self.t = 0
        self.GPIO_PIN = []
        self.status = []
        self.get_GPIO_PIN()
        GPIO_CONT(self.GPIO_PIN,self.status)
        self.timer()
        self.status[7] = 0
        GPIO_CONT(self.GPIO_PIN,self.status)

        while True:
            self.timer()
            pipe_sensor.send(self.update_status(status))
            GPIO_CONT(self.GPIO_PIN,self.status)
            pipe_sensor.send(str("GPIO"))
            status = pipe_GPIO.recv()

    def timer(self,sleep_time=1):
        t = self.t + sleep_time
        while time.time() - self.time_start < self.t + sleep_time:
            time.sleep(0.01)
        self.t = t

    def get_GPIO_PIN(self,status):
        self.device_list = Config().conf.options('GPIO PIN')
        for device in self.device_list:
            self.GPIO_PIN.append(Config().conf.getint('GPIO PIN', device))
            if device == 'run_led' or device == 'data_led':
                self.status.append(1)
            else:
                self.status.append(status.get(device,0))

    def update_status(self, status):
        for i in range(len(self.device_list)-2):
            self.status[i] = status.get(self.device_list[i],0)
        self.status[8] = not self.status[8]

        return_status = {'server_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
        for device in self.device_list:
            if devece in status:
                if status[device] >0:
                    return_status[device] = status[device] - 1
            else:
                continue
        return return_status

if __name__ == '__main__':
    log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_LOG_PATH')))
    UDP_log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_log_PATH')),
                                    str(Config().conf.get('UDP CLIENT','UDP_log_file_path')))
    if not os.path.exists(log_file_path):
        os.mkdir(log_file_path)
    if not os.path.exists(UDP_log_file_path):
        os.mkdir(UDP_log_file_path)

    pipe_sensor = Pipe()
    pipe_GPIO = Pipe()
    pipe_UDP = Pipe()

    mainapp = Process(target=MainAPP, args=(pipe_sensor[1],pipe_UDP[0]))
    temp = Process(target=get_temp, args=(pipe_sensor[0],))
    height = Process(target=get_height, args=(pipe_sensor[0],))
    adc = Process(target=get_ADC_value, args=(pipe_sensor[0],))
    udp_server = Process(target=UDP_server, args=(pipe_sensor[0],pipe_UDP[1],pipe_GPIO[0]))
    sys_timer = Process(target=sys_timer, args=(pipe_sensor[0],pipe_GPIO[1]))

    mainapp.start()
    temp.start()
    height.start()
    adc.start()
    udp_server.start()
    sys_timer.start()

    mainapp.join()
    temp.join()
    height.join()
    adc.join()
    udp_server.join()
    sys_timer.join()

# 结束子进程？
    # p.process.signal(signal.SIGINT)