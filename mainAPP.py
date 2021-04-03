import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Pipe

import os
import socket
import configparser
from Load_config import Config



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


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

class MainAPP(Config):
    def __init__(self, pipe_sensor, pipe_UDP, pipe_GPIO):
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
                if isinstance(data,dict):
                    print(data)
                    # 写入文件
                    log_file.write(str(data))
                    log_file.write('\n')
                    self.status = dict(self.status, **data)
                elif data == "send_to_UDP_server":
                    pipe_UDP.send(self.status)
                elif data == "GPIO":
                    pipe_GPIO.send(self.status)
                else:
                    continue

class UDP_server(Config):
    def __init__(self, pipe_sensor, pipe_UDP):
        self.Get_local_IP()
        self.port = int(Config().conf.get('UDP SERVER','PORT'))
        self.server(pipe_sensor, pipe_UDP)
        self.UDP_log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_LOG_PATH')),
                                            str(Config().conf.get('Defult setting','UDP_log_file_path')),
                                            str(time.strftime("%Y_%m_%d_%H_%M_%S.txt", time.localtime())))

    def Get_local_IP(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            self.Localhost = s.getsockname()[0]
            Config().write('UDP SERVER','LOCALHOST',self.Localhost)
        finally:
            s.close()

    def log(self, ip, port):
        log = 0
        with open(self.UDP_log_file_path, 'a') as udp_log:
            udp_log.write(str(log))
            udp_log.write("\n")

    def server(self, pipe_sensor, pipe_UDP):
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
    def __init__(self,pipe_sensor,pipe_timer):
        GPIO.setmode(GPIO.BCM)
        DHT11_waittime = Config().conf.getint('DHT11','wait_time')
        UR_waittime = Config().conf.getint('UR','wait_time')

        for t in range(DHT11_waittime*UR_waittime):
            GPIO_PIN_list, STATUS_list = pipe_timer.recv()
            for i in range(len(GPIO_PIN_list)-1):
                if STATUS_list[i] == -1:
                    self.Turn_ON(GPIO_PIN_list[i])
                if STATUS_list[i] > 0:
                    self.Turn_ON(GPIO_PIN_list[i])
                if STATUS_list[i] == 0:
                    self.Turn_OFF(GPIO_PIN_list[i])
                else:
                    continue

            if t % DHT11_waittime == 0 :
                self.get_temp(pipe_sensor)
            if t % UR_waittime == 0 :
                # self.get_height(pipe_sensor)
                pass

    def Turn_ON(self,PIN):
        print('OPEN')
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.HIGH)

    def Turn_OFF(self,PIN):
        print('OFF')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.LOW)
        GPIO.cleanup(PIN)

    def Data_LED_Flash(self, on_time=0.2, PIN=Config().conf.getint('GPIO PIN', 'data_led')):
        GPIO.setup(PIN, GPIO.OUT)
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(on_time)
        GPIO.output(PIN, GPIO.LOW)
        GPIO.cleanup(PIN)

    def get_temp(pipe_sensor):
        import units.dht11

        pin=int(Config().conf.get('SENSOR PIN','DHT11'))
        instance = units.dht11.DHT11(pin)
        while True:
            result = instance.read()
            if result.is_valid():
                pipe_sensor.send({'server_time':get_time(),'temperature':result.temperature,'humidity':result.humidity})
                print(result.temperature,result.humidity)
                break
            else:
                continue

    def get_height(pipe_sensor):
        import units.Ultrasonic_ranger

        pin = int(Config().conf.get('SENSOR PIN','UR'))
        Wait_time = float(Config().conf.get('UR','WAIT_TIME'))
        height = units.Ultrasonic_ranger.Get_depth(pin)
        pipe_sensor.send({'server_time':get_time(),'height':height})
    
class sys_timer(Config):
    def __init__(self, pipe_sensor, pipe_GPIO, pipe_timer):
        pipe_sensor.send(str("GPIO"))
        status = pipe_GPIO.recv()
        self.time_start = time.time()
        self.t = 0
        self.GPIO_PIN = []
        self.status = []
        self.get_GPIO_PIN(status)
        pipe_timer.send([self.GPIO_PIN, self.status])
        self.timer()
        self.status[7] = 0
        print("设定dataled关")
        pipe_timer.send([self.GPIO_PIN, self.status])

        while True:
            self.timer()
            pipe_sensor.send(self.update_status(status))
            pipe_timer.send([self.GPIO_PIN, self.status])
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
                print("设定led开")
            else:
                self.status.append(status.get(device,0))

    def update_status(self, status):
        for i in range(len(self.device_list)-2):
            self.status[i] = status.get(self.device_list[i],0)
        self.status[8] = not self.status[8]
        print("设定新状态")

        return_status = {'server_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
        for device in self.device_list:
            if device in status:
                if status[device] >0:
                    return_status[device] = status[device] - 1
            else:
                continue
        return return_status

if __name__ == '__main__':
    log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_LOG_PATH')))
    UDP_log_file_path = os.path.join(str(Config().conf.get('Defult setting','DEFULT_log_PATH')),
                                    str(Config().conf.get('UDP SERVER','UDP_log_file_path')))
    if not os.path.exists(log_file_path):
        os.mkdir(log_file_path)
    if not os.path.exists(UDP_log_file_path):
        os.mkdir(UDP_log_file_path)

    pipe_sensor = Pipe()
    pipe_GPIO = Pipe()
    pipe_UDP = Pipe()
    pipe_timer = Pipe()

    mainapp = Process(target=MainAPP, args=(pipe_sensor[1],pipe_UDP[0],pipe_GPIO[0]))
    adc = Process(target=get_ADC_value, args=(pipe_sensor[0],))
    udp_server = Process(target=UDP_server, args=(pipe_sensor[0],pipe_UDP[1]))
    gpio = Process(target=GPIO_CONT, args=(pipe_sensor[0],pipe_timer[1]))
    sys_timer = Process(target=sys_timer, args=(pipe_sensor[0],pipe_GPIO[1],pipe_timer[0]))

    mainapp.start()
    adc.start()
    udp_server.start()
    gpio.start()
    sys_timer.start()

    mainapp.join()
    adc.join()
    udp_server.join()
    gpio.join()
    sys_timer.join()

# 结束子进程？
    # p.process.signal(signal.SIGINT)