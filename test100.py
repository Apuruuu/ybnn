# import RPi.GPIO as GPIO
import os
import time
from multiprocessing import Process
import paho.mqtt.client as mqtt
import json
import logging
from logging.handlers import RotatingFileHandler
import traceback

from Load_config import Config

class mqtt_pub():
    def __init__(self):
        self.HOST = Config().conf.get('mqtt', 'host')
        self.PORT = Config().conf.getint('mqtt', 'port')
        username = Config().conf.get('mqtt', 'username')
        passwd = Config().conf.get('mqtt', 'passwd')
        self.client = mqtt.Client()
        self.client.username_pw_set(username, passwd)
        try: self.client.connect(self.HOST, self.PORT, 600)
        except: logging.warning(traceback.format_exc())

    def sender(self,data,topic):
        param = json.dumps(data)
        self.client.publish(topic, payload=param, qos=2)  # send message
        try:
            if not topic.split("/")[-1] == 'time+':
                logging.debug('[MQTT]: Send "%s" to MQTT server [%s:%d] with topic "%s"'%(data, self.HOST, self.PORT, topic))
                self.log(topic.split("/")[-1], data)
        except: logging.warning(traceback.format_exc())

    def log(self, device, data):
        # write to file
        with open(save_file_filename,"a") as save_file:
            log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cache = "{:<20s} | {:<10s} | {:s}\n".format(log_time, device, str(data))
            save_file.write(cache) 
            save_file.close()

def server_time(wait_time = 1):
    device_name = 'time'
    _mqtt_pub = mqtt_pub()

    while True:
        try:
            data = {"time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
            topic = Config().conf.get('mqtt','sensor_topic') + device_name
            _mqtt_pub.sender(data, topic)

        except:
            logging.warning(traceback.format_exc())
            continue

        finally: time.sleep(wait_time)

if __name__ == '__main__':
    log_path = os.path.join('log')
    if not os.path.exists(log_path):  # create path when it does not exist
        os.makedirs(log_path)
    # history save path
    save_file_filename = os.path.join(log_path, time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())+'.log')

    SERVER_TIME = Process(target=server_time)
    SERVER_TIME.start()
    SERVER_TIME.join()