# from Load_config import Config

# import RPi.GPIO as GPIO
# import time

def get_ADC_value():
    # import units.ADS1115

    # # read ALL of ADC's channel
    # values = [0]*4
    # for i in range(4):
    #     values[i] = units.ADS1115.readAdc(i) * 6.144 / 32768 # 16bit(2^16) = 65536, half is minus

    # # 计算PH
    # _temperature      = 25.0
    # _acidVoltage      = 2032.44
    # _neutralVoltage   = 1500.0
    # slope     = (7.0-4.0)/((_neutralVoltage-1500.0)/3.0 - (_acidVoltage-1500.0)/3.0)
    # intercept = 7.0 - slope*(_neutralVoltage-1500.0)/3.0
    # PH_value  = slope*(values[0]*1000-1500.0)/3.0+intercept

    # # 计算浊度
    # if values[1] <= 5 and values[1] >= 1 :
    #     turbidity_percentage = 4.41 - (values[1] * 0.8457)
    #     turbidity_NTU = turbidity_percentage * 1300 # 10-6(PPM) = 1ppm = 1mg/L = 0.13NTU(empirical formula), that is: 3.5% = 35000PPM = 35000mg/L = 4550NTU
    # else: turbidity_NTU = -1

    # PH = round(PH_value, 1)
    # TURBIDITY = round(turbidity_NTU, 2)
    # ADC3 = round(values[2], 2)
    # ADC4 = round(values[3], 2)

    return 0,0,0,0

def get_temperature(pin):
    # import units.dht11

    # instance = units.dht11.DHT11(pin)
    # while True:
    #     result = instance.read()
    #     if result.is_valid():
    #         TEMPERATURE = round(result.temperature, 2)
    #         HUMIDITY = round(result.humidity, 2)
    #         return TEMPERATURE, HUMIDITY

    #     else:
    #         continue
    return 0,0

def get_volume(pin):
    # C_width = Config().conf.getint('TROUGH','width')
    # C_depth = Config().conf.getint('TROUGH','depth')
    # sensor_height = Config().conf.getint('TROUGH','height')

    # GPIO.setup(pin, GPIO.OUT)
    # GPIO.output(pin, GPIO.LOW)
    # time.sleep(0.2)
    # GPIO.output(pin, GPIO.HIGH)
    # time.sleep(0.5)
    # GPIO.output(pin, GPIO.LOW)
    # start = time.time()

    # GPIO.setup(pin, GPIO.IN)

    # # get duration from Ultrasonic SIG pin
    # while GPIO.input(pin) == 0:
    #     start = time.time()

    # while GPIO.input(pin) == 1:
    #     end = time.time()

    # time_difference = end-start
    # UR_value = (time_difference * 340290) / 2

    # HEIGHT = round(sensor_height - UR_value, 2)
    # VOLUME = round((C_depth * C_width * HEIGHT / 1000), 2)

    return 0,0

def get_luminosity():
    # import units.tsl2591

    # tsl = units.tsl2591.Tsl2591()  # initialize

    # FULL_SPECTRUM, IR_SPECTRUM = tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
    # LUMINOSITY = tsl.calculate_lux(FULL_SPECTRUM, IR_SPECTRUM)  # convert raw values to lux

    return 0,0,0