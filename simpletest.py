import time
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 8

def avg(a,b,c,d):
    d = a+b+c+d
    d = d / 4
    return d

while True:
     values = [0]*4
     for i in range(4):
         values[i] = adc.read_adc(i, gain=GAIN) * 0.512 / 2**15 
    
     print('AVG: %f |   |NF %f |R %f |G %f |B %f |' %(avg(values[0],values[1],values[2],values[3]),values[0],values[1],values[2],values[3]))
     
     time.sleep(0.1)