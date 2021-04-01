
import time
import os
import socket
import configparser
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


class MainAPP(Config):
    def __init__(self):
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
        while True:
            self.UDP_sender(self.stauts)
            time.sleep(2)


    def UDP_sender(self, data):
        IP_cache_file_path = os.path.join(Config().conf.get('Defult setting','DEFULT_CACHE_PATH'),
                                        Config().conf.get('Defult setting','DEFULT_IP_CACHE_FILE'))
        IP_cache = eval(open(IP_cache_file_path).read())
        
        for IP_PORT in IP_cache:
            udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            local_addr = ("",7890)
            udp_socket.bind(local_addr)
            
            send_data = str(self.stauts)
            udp_socket.sendto(send_data.encode("utf-8"),(IP_PORT[0],IP_PORT[1]))
            udp_socket.close()

if __name__ == '__main__':
    MainAPP()