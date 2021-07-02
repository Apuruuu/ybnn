import os
import time
from multiprocessing import Process
import paho.mqtt.client as mqtt
import json
import logging
from logging.handlers import RotatingFileHandler
import traceback

# import sensor_get
from Load_config import Config


# 切换工作目录至文件目录
root_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(root_path)

log_path = os.path.join(root_path,'log')
print(os.getcwd())
if not os.path.exists(log_path):  # create path when it does not exist
    os.makedirs(log_path)
# history save path

save_file_filename = os.path.join(log_path, time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())+'.log')
with open(save_file_filename,"w") as save_file:
    save_file.write('') 
    save_file.close()


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
    def __init__(self):
        self.HOST = Config().conf.get('mqtt', 'host')
        self.PORT = Config().conf.getint('mqtt', 'port')
        username = Config().conf.get('mqtt', 'username')
        passwd = Config().conf.get('mqtt', 'passwd')
        print(self.HOST, self.PORT, username, passwd)
        self.client = mqtt.Client()
        self.client.username_pw_set(username, passwd)
        try: self.client.connect(self.HOST, self.PORT, 600)
        except: logging.warning(traceback.format_exc())

    def sender(self,data,topic):
        param = json.dumps(data)
        self.client.publish(topic, payload=param, qos=2)  # send message
        try:
            if not topic.split("/")[-1] == 'time1':
                logging.debug('[MQTT]: Send "%s" to MQTT server [%s:%d] with topic "%s"'%(data, self.HOST, self.PORT, topic))
                self.log(topic.split("/")[-1], data)
        except: logging.warning(traceback.format_exc())

    def log(self, device, data):
        # write to file
        # global save_file_filename
        print(save_file_filename)
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
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

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
    
    SERVER_TIME = Process(target=server_time, args=())

    SERVER_TIME.start()

    SERVER_TIME.join()
