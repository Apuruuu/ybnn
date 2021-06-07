import RPi.GPIO as GPIO
import time
from multiprocessing import Process
import paho.mqtt.client as mqtt
import json

from Load_config import Config

class mqtt_pub():
    def __init__(self):
        self.HOST = Config().conf.get('mqtt', 'host')
        self.PORT = Config().conf.getint('mqtt', 'port')
        username = Config().conf.get('mqtt', 'username')
        passwd = Config().conf.get('mqtt', 'passwd')
        self.client = mqtt.Client()
        self.client.username_pw_set(username, passwd)
        self.client.connect(self.HOST, self.PORT, 60)

    def sender(self,data,topic):
        param = json.dumps(data)
        self.client.publish(topic, payload=param, qos=0)     # 发送消息
        print('[MQTT]: Send "%s" to MQTT server [%s:%d] with topic "%s"'%(data, self.HOST, self.PORT, topic))

def server_time():
    _mqtt_pub = mqtt_pub()
    topic = "homeassistant/sensor/time"

    while True:
        data = {"time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
        _mqtt_pub.sender(data, topic)
        time.sleep(1)

def get_ADC_value():
    import units.ADS1x15

    adc = units.ADS1x15.ADS1115()
    GAIN = Config().conf.getint('ADC','GAIN')

    _mqtt_pub = mqtt_pub()
    topic = Config().conf.get('ADC','topic')
    Wait_time = float(Config().conf.get('ADC','WAIT_TIME'))

    while True:
        # 读取ADC所有信道的值
        values = [0]*4
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN)
        # ADC debug
        # print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))

        data = {'PH':values[0], 'turbidity':values[1], 'ADC3_A2':values[2], 'ADC4_A3':values[3]}
        _mqtt_pub.sender(data, topic)
        time.sleep(Wait_time)

def get_temperature():
    import units.dht11

    pin=int(Config().conf.get('SENSOR PIN','DHT11'))
    instance = units.dht11.DHT11(pin)

    _mqtt_pub = mqtt_pub()
    topic = Config().conf.get('DHT11','topic')
    Wait_time = float(Config().conf.get('DHT11','WAIT_TIME'))

    while True:
        result = instance.read()
        if result.is_valid():
            data = {'temperature':result.temperature, 'humidity':result.humidity}
            _mqtt_pub.sender(data, topic)
            time.sleep(Wait_time)
        else:
            continue

def get_height():
    import units.Ultrasonic_ranger

    pin = Config().conf.getint('SENSOR PIN','UR')

    C_width = int(Config().conf.get('UR','width'))
    C_depth = int(Config().conf.get('UR','depth'))
    C_height = int(Config().conf.get('UR','height'))

    _mqtt_pub = mqtt_pub()
    topic = Config().conf.get('UR','topic')
    Wait_time = float(Config().conf.get('UR','WAIT_TIME'))
    while True:
        height = units.Ultrasonic_ranger.Get_depth(pin)
        volume = (C_depth * C_width * (C_height-height)) / 1000
        data = {'height':height, 'volume':volume}
        _mqtt_pub.sender(data, topic)
        time.sleep(Wait_time)

def get_luminosity():
    import units.tsl2591

    tsl = units.tsl2591.Tsl2591()  # initialize

    _mqtt_pub = mqtt_pub()
    topic = Config().conf.get('LUX','topic')
    Wait_time = float(Config().conf.get('LUX','WAIT_TIME'))
    while True:
        full_spectrum, ir_spectrum = tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
        luminosity = float("{:.2f}".format(tsl.calculate_lux(full_spectrum, ir_spectrum)))  # convert raw values to lux
        data = {'luminosity':luminosity, 'full_spectrum':full_spectrum, 'ir_spectrum': ir_spectrum}
        _mqtt_pub.sender(data, topic)
        time.sleep(Wait_time)

class mqtt_sub():
    def __init__(self):
        HOST = Config().conf.get('mqtt', 'host')
        PORT = Config().conf.getint('mqtt', 'port')
        username = Config().conf.get('mqtt', 'username')
        passwd = Config().conf.get('mqtt', 'passwd')
        command_topic = str(Config().conf.get('mqtt', 'root_topic')) + '#'

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code: " + str(rc))

        def on_message(client, userdata, msg):
            self.controller(msg.topic, msg.payload)
        
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password=passwd)
        self.client.on_connect = on_connect
        self.client.connect(HOST, PORT, 600) # 600为keepalive的时间间隔
        self.client.subscribe(command_topic, qos=0)
        
        self.client.on_message = on_message
        self.client.loop_forever() # 保持连接

    def controller(self, topic, data):
        mode = topic.split("/")[-1]
        device = topic.split("/")[-2]
        value = data.decode('utf-8')

        def set_device(GPIO_PIN, value):
            GPIO.setup(GPIO_PIN, GPIO.OUT)
            if value == 1:
                GPIO.output(GPIO_PIN, GPIO.HIGH)
            elif value == 0:
                GPIO.output(GPIO_PIN, GPIO.LOW)
            return True

        if mode == 'set':
            GPIO_PIN = Config().conf.getint('GPIO PIN',device)
            print('device: %s on Gpin(%d)[%s] set to %d'%(Config().conf.get('devices',device),GPIO_PIN,device,value))
            if set_device(GPIO_PIN, value):
                state_topic = str(Config().conf.get('mqtt', 'root_topic')) + str(device)
                _mqtt_pub=mqtt_pub()
                _mqtt_pub.sender(int(value), state_topic)

def run_led():
    GPIO_PIN = Config().conf.getint('GPIO PIN','run_led')
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    while True:
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(GPIO_PIN, GPIO.LOW)
        time.sleep(1)

def data_led(value):
    GPIO_PIN = Config().conf.getint('GPIO PIN','data_led')
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    if value == 1:
        GPIO.output(GPIO_PIN, GPIO.HIGH)
    elif value == 0:
        GPIO.output(GPIO_PIN, GPIO.LOW)

if __name__ == '__main__':
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    # wait network
    print("waiting network 30 Seconds")
    for i in range(3):
        print((i+1)*10, Seconds)
        time.sleep(10)

    SERVER_TIME = Process(target=server_time, args=())
    GET_ADC_VALUE = Process(target=get_ADC_value, args=())
    GET_TEMPERATURE = Process(target=get_temperature, args=())
    GET_LUMINOSITY = Process(target=get_luminosity, args=())
    GET_HEIGHT = Process(target=get_height, args=())
    MQTT_SUB = Process(target=mqtt_sub, args=())
    RUN_LED = Process(target=run_led, args=())
    

    SERVER_TIME.start()
    GET_ADC_VALUE.start()
    GET_TEMPERATURE.start()
    GET_LUMINOSITY.start()
    GET_HEIGHT.start()
    MQTT_SUB.start()
    RUN_LED.start()

    SERVER_TIME.join()
    GET_ADC_VALUE.join()
    GET_TEMPERATURE.join()
    GET_LUMINOSITY.join()
    GET_HEIGHT.join()
    MQTT_SUB.join()
    RUN_LED.join()