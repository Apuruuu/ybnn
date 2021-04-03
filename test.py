from Load_config import Config
import time

class sys_timer(Config):
    def __init__(self):

        status = {'server_time':'N/A',
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
        self.GPIO_PIN = []
        self.status = []
        self.get_GPIO_PIN(status)
        print(self.GPIO_PIN)
        print(self.status)

        while True:


            self.status = []
            self.pickup(status)
            self.run_LED()



            time.sleep(1)

    def get_GPIO_PIN(self,status):
        self.device_list = Config().conf.options('GPIO PIN')
        for device in self.device_list:
            self.GPIO_PIN.append(Config().conf.getint('GPIO PIN', device))
            if device == 'run_led' or device == 'data_led':
                self.status.append(1)
            else:
                self.status.append(status.get(device,0))

                



    
    def pickup(self, status):

        self.status[0] = status['light']
        self.status[1] = status['pump_air']
        self.status[2] = status['pump_1']
        self.status[3] = status['pump_2']
        self.status[4] = status['magnetic_stitter']
        self.status[5] = 0
        self.status[6] = 0
        self.status[7] = 0

        status['light'] -= 1
        status['pump_air'] -= 1
        status['pump_1'] -= 1
        status['pump_2'] -= 1
        status['magnetic_stitter'] -= 1

    def run_LED(self):
        self.status[8] = not self.status[8]


sys_timer()