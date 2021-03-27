import json
import os

import configparser


class Config(object):
    def __init__(self):
        self.config_file_path = 'config.cfg'
        self.load_config()

    def load_config(self):
        # 检测是否存在config.cfg文件
        if not os.walk(self.config_file_path):
            json_file=open(self.config_file_path)
            # 写入默认配置文件

        # 读取config文件
        self.conf = configparser.ConfigParser()
        self.conf.read(self.config_file_path)