import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Pipe

import socket
import configparser

# 初始化GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

class Config(object):
    def __init__(self):
        self.config_file_path = 'config.cfg'
        if not os.walk(self.config_file_path):
            with open(self.config_file_path) as config_file:
                # 写入默认配置文件
                config_file.close()
                pass
        self.read()

    # 读取config文件
    def read(self):
        self.conf = configparser.ConfigParser()
        self.conf.read(self.config_file_path)

    def write(self,name1,name2,value):
        self.conf.set(name1, name2, value)
        print(self.conf.get('UDP server','LOCALHOST'))
        with open(self.config_file_path,'w') as config_file:
            self.conf.write(config_file)
            config_file.close()

def get_temp(pipe_sensor):
    import units.dht11

    pin=int(Config().conf.get('GPIO_PIN','DHT11'))
    instance = units.dht11.DHT11(pin)
    Wait_time = float(Config().conf.get('DHT11','WAIT_TIME'))

    while True:
        result = instance.read()
        if result.is_valid():
            pipe_sensor.send({'time':get_time(),
                                'temperature':result.temperature,
                                'humidity':result.humidity})
            print(result.temperature,result.humidity)
        else:
            pipe_sensor.send({'time':get_time(),
                                'temperature':"N/A",
                                'humidity':"N/A"})
            print('nodata')
        time.sleep(Wait_time)

def get_ADC_value(pipe_sensor):
    import units.ADS1x15

    adc = units.ADS1x15.ADS1115()
    GAIN = Config().conf.get('ADC','GAIN')
    Wait_time = float(Config().conf.get('ADC','WAIT_TIME'))

    while True:
        # 读取ADC所有信道的值
        values = [0]*4
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN)
        print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
        pipe_sensor.send({'time':get_time(),
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
        pipe_sensor.send({'time':get_time(),
                            'height':height})
        time.sleep(Wait_time)

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

class MainAPP(Config):
    def __init__(self, pipe_sensor):
        self.stauts = {'time':'N/A',
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

        cache_file_path = os.path.join(str(Config().conf.get('DEFULT_CACHE_PATH')),
                                        str(get_time())+'.txt')
        with open(cache_file_path, 'a') as cache_file:
            while True:
                data = pipe_sensor.recv()
                if isinstance(data,dict):
                    # 写入文件
                    cache_file.write(data)
                    cache_file.write('\n')
                    self.stauts = dict(self.stauts, **data)
                    self.UDP_sender(data)
                else:
                    continue

    def UDP_sender(self, data):
        IP_cache_file_path = os.path.join(Config().conf.get('Defult setting','DEFULT_CACHE_PATH'),
                                        Config().conf.get('Defult setting','DEFULT_IP_CACHE_FILE'))
        IP_cache = eval(open(IP_cache_file_path).read())
        
        for IP_PORT in IP_cache:
            if IP_PORT[0] == None or IP_PORT[1] == None:
                continue
            udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            local_addr = ("",7890)
            udp_socket.bind(local_addr)
            
            send_data = str(self.stauts)
            udp_socket.sendto(send_data.encode("utf-8"),(IP_PORT[0],IP_PORT[1]))
            udp_socket.close()

class UDP_server(Config):
    def __init__(self):
        self.Get_local_IP()
        print("Localhost_IP = ",self.Localhost)

        self.ip_cache = []
        self.add_new_client(None,None)

        self.port = int(Config().conf.get('UDP server','PORT'))
        self.send_to_IP = [] #[[IP,port],...]

    def Get_local_IP(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            self.Localhost = s.getsockname()[0]
            Config().write('UDP server','LOCALHOST',self.Localhost)
            print('Localhost =', self.Localhost,":",Config().conf.get('UDP server','PORT'))

        finally:
            s.close()

    def server(self):
        server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server.bind((self.Localhost, self.port)) #绑定服务器的ip和端口
        data=server.recv(1024) #一次接收1024字节
        print(data.decode())# decode()解码收到的字节

    def add_new_client(self, ip, port):
        # 添加新客户端IP
        if [ip, port] not in self.ip_cache:
            self.ip_cache.append([ip, port])
            IP_cache_file_path = os.path.join(Config().conf.get('Defult setting','DEFULT_CACHE_PATH'),
                                        Config().conf.get('Defult setting','DEFULT_IP_CACHE_FILE'))
            with open(IP_cache_file_path, 'w') as ip_cache_file:
                ip_cache_file.write(str(self.ip_cache))

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
    pipe_GPIO = Pipe()

    mainapp = Process(target=MainAPP, args=(pipe_sensor[1],pipe_GPIO[1]))
    temp = Process(target=get_temp, args=(pipe_sensor[0],))
    height = Process(target=get_height, args=(pipe_sensor[0],))
    adc = Process(target=get_ADC_value, args=(pipe_sensor[0],))
    udp_server = Process(target=UDP_server, args=(pipe_GPIO[0],))
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