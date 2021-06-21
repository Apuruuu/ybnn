
import units.ADS1115
import time

_temperature      = 25.0
_acidVoltage      = 2032.44
_neutralVoltage   = 1500.0

while True:
    # read ALL of ADC's channel
    values = [0]*4
    for i in range(4):
        values[i] = units.ADS1115.readAdc(i) * 6.144 / 32768 # 16bit(2^16) = 65536, half is minus

    # 计算PH
    slope     = (7.0-4.0)/((_neutralVoltage-1500.0)/3.0 - (_acidVoltage-1500.0)/3.0)
    intercept = 7.0 - slope*(_neutralVoltage-1500.0)/3.0
    PH_value  = slope*(values[0]*1000-1500.0)/3.0+intercept

    # PH_value = values[0] * 3.5

    # 计算浊度
    if values[1] <= 5 and values[1] >= 1 :
        turbidity_percentage = 4.41 - (values[1] * 0.8457)
        turbidity_NTU = turbidity_percentage * 1300 # 10-6(PPM) = 1ppm = 1mg/L = 0.13NTU(empirical formula), that is: 3.5% = 35000PPM = 35000mg/L = 4550NTU
    else: turbidity_NTU = -1

    data = {'PH':float("{:.2f}".format(PH_value)),
                'turbidity':float("{:.2f}".format(turbidity_NTU)),
                'ADC3_A2':float("{:.2f}".format(values[2])),
                'ADC4_A3':float("{:.2f}".format(values[3]))}
    print(data)
    time.sleep(1)