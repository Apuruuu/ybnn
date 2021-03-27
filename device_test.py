import socket
import os
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

class UDP_sender():
    def __init__(self):
        message = MainAPP.stauts
        self.sender(message)

    # UDP发送端
    def sender(self, message):
        buffersize=1024
        Sender = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        for IP, port in UDP_server.send_to_IP:
            Sender.sendto(message.encode(),(IP,port))

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


if __name__ == '__main__':
    UDP_server()
    






# 结束子进程？
    # p.process.signal(signal.SIGINT)