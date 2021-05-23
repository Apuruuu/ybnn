from os import name
import time
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

if __name__ == '__main__':
    server_time()