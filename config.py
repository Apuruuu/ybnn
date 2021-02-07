import json
import os

class Config(object):
    def __init__(self):
        self.load_config



    def load_config(self):
        if not os.walk(config_file_path):
            json_file=open(config_file_path)
            # 写入默认配置文件

        # open json file
        json_file=json.load(open(self.config_file_path))