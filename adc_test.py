# Sample code for ESP8266 & ESP32, Micropython.org firmware
from machine import I2C, Pin, Timer
import ADS1x15
from array import array

addr = 72
gain = 1
_BUFFERSIZE = const(512)

data = array("h", (0 for _ in range(_BUFFERSIZE)))
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
# for the Pycom branch or Micropython, use:
# i2c = I2C()
ads = ads1x15.ADS1115(i2c, addr, gain)
#
# Interrupt service routine for data acquisition
# activated by a pin level interrupt
#
def sample_auto(x, adc = ads.alert_read, data = data):
    global index_put
    if index_put < _BUFFERSIZE:
        data[index_put] = adc()
        index_put += 1

index_put = 0

irq_pin = Pin(13, Pin.IN, Pin.PULL_UP)
ads.conversion_start(5, 0)

irq_pin.irq(trigger=Pin.IRQ_FALLING, handler=sample_auto)

while index_put < _BUFFERSIZE:
    pass

irq_pin.irq(handler=None)
#
# at that point data contains 512 samples acquired at the given rate
#