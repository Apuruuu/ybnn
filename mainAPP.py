import RPi.GPIO as GPIO
import os
import time
from multiprocessing import Process
import paho.mqtt.client as mqtt
import json
import logging
from logging.handlers import RotatingFileHandler
import traceback

import sensor_get
from Load_config import Config


def Web_server():
    import http.server, socketserver

    try:
        PORT = Config().conf.getint('WEB','port')
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            logging.info("Webserver at port", PORT)
            httpd.serve_forever()
    except: logging.warning(traceback.format_exc())
    finally:logging.warning('Web server stopped')

class mqtt_pub():
    def __init__(self, save_file_filename):
        self.HOST = Config().conf.get('mqtt', 'host')
        self.PORT = Config().conf.getint('mqtt', 'port')
        username = Config().conf.get('mqtt', 'username')
        passwd = Config().conf.get('mqtt', 'passwd')
        self.save_file_name = save_file_filename
        self.client = mqtt.Client()
        self.client.username_pw_set(username, passwd)
        try: self.client.connect(self.HOST, self.PORT, 600)
        except: logging.warning(traceback.format_exc())

    def sender(self,data,topic):
        try:
            if not topic.split("/")[-1] == 'time':
                self.log(topic.split("/")[-1], data)
                param = json.dumps(data)
                self.client.publish(topic, payload=param, qos=2)  # send message
                logging.debug('[MQTT]: Send "%s" to MQTT server [%s:%d] with topic "%s"'%(data, self.HOST, self.PORT, topic))
        except: logging.warning(traceback.format_exc())

    def log(self, device, data):
        # write to file
        with open(self.save_file_filename,"a") as save_file:
            log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cache = "{:<20s} | {:<10s} | {:s}\n".format(log_time, device, str(data))
            save_file.write(cache) 
            save_file.close()

class mqtt_sub():
    def __init__(self):
        self.command_topic = str(Config().conf.get('mqtt', 'switch_topic')) + '#'
        self.status_topic = str(Config().conf.get('mqtt', 'status_topic'))
        self._mqtt_pub=mqtt_pub()
        self.mqtt_sub_init()
    
    def mqtt_sub_init(self):
        HOST = Config().conf.get('mqtt', 'host')
        PORT = Config().conf.getint('mqtt', 'port')
        username = Config().conf.get('mqtt', 'username')
        passwd = Config().conf.get('mqtt', 'passwd')
        self.client = mqtt.Client(client_id="pi", clean_session=False)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.username_pw_set(username, password=passwd)

        self.client.connect(HOST, PORT, keepalive=600)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code: " + str(rc))
        self.client.subscribe(self.command_topic, qos=2)

    def on_message(self, client, userdata, msg):
        self.controller(msg.topic, msg.payload)

    def on_disconnect(self, client, userdata, rc):
        logging.info("Disconnected from MQTT server with code: %s" % rc)
        while rc != 0:
            time.sleep(2)
            try:
                logging.info("Try reconnecting...")
                rc = self.client.reconnect()
            except:
                logging.warning(traceback.format_exc())
                continue

            finally: self.client.loop_stop()

    def controller(self, topic, data):
        action = topic.split("/")[-1]
        device = topic.split("/")[-2]
        value = int(data.decode('utf-8'))

        def set_device(GPIO_PIN, value, invert=True):
            GPIO.setup(GPIO_PIN, GPIO.OUT)
            if invert:
                value = 1 - value
            GPIO.output(GPIO_PIN, value)

        if action == 'set':
            GPIO_PIN = Config().conf.getint('GPIO PIN',device)
            logging.debug('device: %s on Gpin(%d)[%s] set to %d'%(Config().conf.get('devices name',device),GPIO_PIN,device,value))
            if set_device(GPIO_PIN, value):
                _state_topic = self.status_topic + str(device)
                self._mqtt_pub.sender(value, _state_topic)

def server_time(save_file_filename, wait_time = 1):
    device_name = 'time'
    _mqtt_pub = mqtt_pub(save_file_filename)

    while True:
        try:
            data = {"time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
            topic = Config().conf.get('mqtt','sensor_topic') + device_name
            _mqtt_pub.sender(data, topic)

        except:
            logging.warning(traceback.format_exc())
            continue

        finally: time.sleep(wait_time)

def get_ADC_value(save_file_filename):
    device_name = 'ads1115'
    _mqtt_pub = mqtt_pub(save_file_filename)

    while True:
        try:
            PH, TURBIDITY, ADC3, ADC4 = sensor_get.get_ADC_value()
            data = {'PH':PH, 'turbidity':TURBIDITY, 'ADC3_A2':ADC3, 'ADC4_A3':ADC4}
            topic = Config().conf.get('mqtt','sensor_topic') + device_name
            _mqtt_pub.sender(data, topic)

        except:
            logging.warning(traceback.format_exc())
            continue

        finally: time.sleep(Config().conf.getint('WAIT_TIME',device_name))

def get_temperature(save_file_filename):
    device_name = 'dht11'
    _mqtt_pub = mqtt_pub(save_file_filename)

    while True:
        try:
            pin = Config().conf.getint('SENSOR_GPIN','DHT11')
            TEMPERATURE, HUMIDITY = sensor_get.get_temperature(pin)
            data = {'temperature':TEMPERATURE, 'humidity':HUMIDITY}
            topic = Config().conf.get('mqtt','sensor_topic') + device_name
            _mqtt_pub.sender(data, topic)

        except:
            logging.warning(traceback.format_exc())
            continue

        finally: time.sleep(Config().conf.getint('WAIT_TIME',device_name))

def get_height(save_file_filename):
    device_name = 'height'
    _mqtt_pub = mqtt_pub(save_file_filename)

    while True:        
        try:
            pin = Config().conf.getint('SENSOR_GPIN','UR')
            HEIGHT, VOLUME = sensor_get.get_volume(pin)
            data = {'height':HEIGHT, 'volume':VOLUME}
            topic = Config().conf.get('mqtt','sensor_topic') + device_name
            _mqtt_pub.sender(data, topic)

        except:
            logging.warning(traceback.format_exc())
            continue

        finally:
            # turn OFF the pump_in when over the MAX level
            height_max = int(Config().conf.get('TROUGH','height_max'))
            if HEIGHT > height_max:
                _mqtt_pub.sender(0, 'homeassistant/switch/switch3/set')
                _mqtt_pub.sender(1, 'homeassistant/switch/warn_led/set')
            time.sleep(Config().conf.getint('WAIT_TIME',device_name))

def get_luminosity(save_file_filename):
    device_name = 'lux'
    _mqtt_pub = mqtt_pub(save_file_filename)

    while True:        
        try:
            FULL, IR, LUMINOSITY = sensor_get.get_luminosity()
            data = {'luminosity':LUMINOSITY, 'full_spectrum':FULL, 'ir_spectrum': IR}
            topic = Config().conf.get('mqtt','sensor_topic') + device_name
            _mqtt_pub.sender(data, topic)

        except:
            logging.warning(traceback.format_exc())
            continue

        finally: time.sleep(Config().conf.getint('WAIT_TIME',device_name))

def run_led():
    while True:
        try:
            GPIO_PIN = Config().conf.getint('LED PIN','run_led')
            GPIO.setup(GPIO_PIN, GPIO.OUT)
            status = 0
            while True:
                GPIO.output(GPIO_PIN, 1 - status)
                time.sleep(1)
        except: logging.warning(traceback.format_exc())
        finally: time.sleep(10)

def get_webservertime(host):
    import http.client

    try:
        logging.debug('setting system time')
        conn=http.client.HTTPConnection(host)
        conn.request("GET", "/")
        r=conn.getresponse()
        ts=  r.getheader('date') # get HEAD
        ltime= time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
        # change time to Japan localtime
        ttime=time.localtime(time.mktime(ltime)+9*60*60)
        dat="sudo date -s %u/%02u/%02u"%(ttime.tm_year,ttime.tm_mon,ttime.tm_mday)
        tm="sudo date -s %02u:%02u:%02u"%(ttime.tm_hour,ttime.tm_min,ttime.tm_sec)
        logging.debug('Internet time %u/%02u/%02u %02u:%02u:%02u'%(ttime.tm_year,
                ttime.tm_mon,ttime.tm_mday, ttime.tm_hour,ttime.tm_min,ttime.tm_sec))
        os.system(dat)
        os.system(tm)
    except: logging.warning(traceback.format_exc())
    finally: logging.info('Localtime set to  %u/%02u/%02u %02u:%02u:%02u'%(ttime.tm_year,
                    ttime.tm_mon,ttime.tm_mday, ttime.tm_hour,ttime.tm_min,ttime.tm_sec))

def GPIO_INIT():
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Config().conf.getint('LED PIN','run_led'), GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(Config().conf.getint('LED PIN','warn_led'), GPIO.OUT, initial=GPIO.HIGH)
    except:
        logging.warning(traceback.format_exc())

if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    import argparse
    parser = argparse.ArgumentParser(prog='ybnn')
    parser.add_argument('--loglevel','-ll', metavar='LL', default='info', type=str, help='Log leve. I/info[default] <N/none><C/critical><E/error><W/warning><I/info><D/debug>')
    parser.add_argument('--log','-l', metavar='L', default=True, type=bool, help='Save sensors data (default True)')
    parser.add_argument('--fast','-f', metavar='F', default=False, type=bool, help='Run without wait_network.')
    args = parser.parse_args()

    # ###############################################
    # LOG LEVEL:
    # N or none:     Nothing will be logged
    # C or critical: The most critical information
    # E or error:    Errors
    # W or warning:  Child process error
    # I or info:     General info
    # D or debug:    All of MQTT message
    # ###############################################

    # 切换工作目录至文件目录
    root_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(root_path)

    logger = logging.getLogger(__name__)
    _format=logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')

    # 控制台输出
    CLI_output = logging.StreamHandler()  
    CLI_output.setLevel(logging.DEBUG)  
    CLI_output.setFormatter(_format)
    logger.addHandler(CLI_output)

    # 控制台输出保存到文件
    _log_level = args.loglevel
    if not _log_level == 'N' or not _log_level == "none":
        log2file = RotatingFileHandler("CLI-LOG.txt",maxBytes = 1*1024,backupCount = 5)
        if _log_level == 'C' or _log_level == "critical":log2file.setLevel(logging.CRITICAL)
        elif _log_level == 'E' or _log_level == "error":log2file.setLevel(logging.ERROR)
        elif _log_level == 'W' or _log_level == "warning":log2file.setLevel(logging.WARNING)
        elif _log_level == 'I' or _log_level == "info":log2file.setLevel(logging.INFO)
        elif _log_level == 'D' or _log_level == "debug":log2file.setLevel(logging.DEBUG)
        log2file.setFormatter(_format)
        logger.addHandler(log2file)

    logger.info("Log Level = %s"%(_log_level))  
    logger.debug("Version = 1.0")

    # wait network
    if not args.fast:
        logger.debug("waiting network 30 Seconds")
        time.sleep(30)

    log_path = os.path.join('log')
    if not os.path.exists(log_path):  # create path when it does not exist
        os.makedirs(log_path)
    # history save path
    save_file_filename = os.path.join(log_path, time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())+'.log')
    
    GPIO_INIT()

    # set time to network(default Google.com)
    get_webservertime('www.google.com')
    GPIO.setup(Config().conf.getint('LED PIN','warn_led'), GPIO.OUT, initial=GPIO.LOW)

    SERVER_TIME = Process(target=server_time, args=(save_file_filename,))
    GET_ADC_VALUE = Process(target=get_ADC_value, args=(save_file_filename,))
    GET_TEMPERATURE = Process(target=get_temperature, args=(save_file_filename,))
    GET_LUMINOSITY = Process(target=get_luminosity, args=(save_file_filename,))
    GET_HEIGHT = Process(target=get_height, args=(save_file_filename,))
    MQTT_SUB = Process(target=mqtt_sub, args=())
    RUN_LED = Process(target=run_led, args=())
    WEB_SERVER = Process(target=Web_server, args=())

    SERVER_TIME.start()
    GET_ADC_VALUE.start()
    GET_TEMPERATURE.start()
    GET_LUMINOSITY.start()
    GET_HEIGHT.start()
    MQTT_SUB.start()
    RUN_LED.start()
    WEB_SERVER.start()

    SERVER_TIME.join()
    GET_ADC_VALUE.join()
    GET_TEMPERATURE.join()
    GET_LUMINOSITY.join()
    GET_HEIGHT.join()
    MQTT_SUB.join()
    RUN_LED.join()
    WEB_SERVER.join()