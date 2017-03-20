from flask import Flask
from flask_ask import Ask, statement, convert_errors
import logging


app = Flask(__name__)
ask = Ask(app, '/')

fname = '/home/pi/Logs/temp'
avail_rooms = ['bedroom', 'mainbedroom']
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

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

    port = 5050
    app.run(host='0.0.0.0', port=port)
