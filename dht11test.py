import dht11
import Adafruit_ADS1x15

def get_temp(pipe_sensor, pin=19):
    instance = dht11.DHT11(pin)
    while True:
        result = instance.read()

        print('temperature',result.temperature, 'humidity',result.humidity)

        time.sleep(1)