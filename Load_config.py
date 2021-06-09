import os
import configparser

class Config(object):
    def __init__(self):
        self.config_file_path = os.path.join('home','pi','ybnn','config.cfg')
        if not os.walk(self.config_file_path):
            self.create_default_config_file()
        self.read()

    # 读取config文件
    def read(self):
        self.conf = configparser.ConfigParser()
        self.conf.read(self.config_file_path)

    def write(self,name1,name2,value):
        self.conf.set(name1, name2, value)
        print(self.conf.get('UDP SERVER','LOCALHOST'))
        with open(self.config_file_path,'w') as config_file:
            self.conf.write(config_file)
            config_file.close()

    def create_default_config_file(self):
        with open(self.config_file_path) as config_file:
                # 写入默认配置文件
                config_file.close()
                pass