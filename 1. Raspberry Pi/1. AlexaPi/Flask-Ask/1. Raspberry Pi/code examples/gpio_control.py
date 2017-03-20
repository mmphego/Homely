from flask import Flask
from flask_ask import Ask, statement, convert_errors
import RPi.GPIO as GPIO
import logging

GPIO.setmode(GPIO.BCM)

app = Flask(__name__)
ask = Ask(app, '/')

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.intent('GPIOControlIntent', mapping={'status': 'status', 'pin': 'pin'})
def gpio_control(status, pin):

    try:
        pinNum = int(pin)
    except Exception as e:
        return statement('Pin number not valid.')

    GPIO.setup(pinNum, GPIO.OUT)

    if status in ['on', 'high']:    GPIO.output(pinNum, GPIO.LOW)
    if status in ['off', 'low']:    GPIO.output(pinNum, GPIO.HIGH)

    return statement('Turning pin {} {}'.format(pin, status))

@ask.intent('TempMonitorIntent', mapping={'room': 'room'})
def temp_monitor(room):

    try:
        with open(fname) as f:
            content = f.readlines()
        content = eval([x.strip('\n') for x in content][0])
        temp, hum, light = content
    except Exception as e:
        return statement('Sorry, I could not retrieve the temperature and humidity data.')


    if room in avail_rooms:
        return statement('The current temperature in the {} is {} degrees celcius, '
                         'humidity of {}% and luminosity of {}%'.format(
                          room, temp, hum, float(light / 10)))

    if room not in avail_rooms:
        return statement('I am not sure which room you meant, available rooms are {}'.format(
            ', '.join(avail_rooms)))


if __name__ == '__main__':

    port = 5050 #the custom port you want
    app.run(host='0.0.0.0', port=port)
