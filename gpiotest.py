import RPi.GPIO as GPIO

GPIO_PIN_list = [14, 15, 18, 23, 24, 25, 8, 7, 4, 22]
for PIN in GPIO_PIN_list:
    GPIO.setup(PIN, GPIO.OUT)
    GPIO.output(PIN, GPIO.HIGH)

