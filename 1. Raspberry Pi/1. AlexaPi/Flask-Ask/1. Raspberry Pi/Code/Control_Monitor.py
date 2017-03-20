import RPi.GPIO as GPIO
import feedparser
import logging
import googlemaps
import psutil
import os
import time
import signal
from datetime import datetime
from flask import Flask
from flask_ask import Ask, statement, convert_errors
from subprocess import check_output

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

app = Flask(__name__)
ask = Ask(app, '/')

fname = '/home/pi/Logs/temp'
stationLink =    'http://edge.iono.fm/xice/touchcentral_live_medium.aac'
audioplayer = 'mplayer'
options_ =  ' < /dev/null > /dev/null 2>&1 &'
avail_rooms = ['bedroom', 'mainbedroom', 'seating room', 'tv room', 'kids bedroom', 'other bedroom',
               'kitchen']
rssfeed = 'http://feeds.news24.com/articles/News24/SouthAfrica/rss'
headlinesCount = 5

googlemaps_api = 'AIzaSyDcBuwDu4Jp0eIHHG4r3EtfYYF47M5WNrs'

presenceDetect = {"Mpho" : "bc:44:86:dd:8c:fc", "Tshilidzi" : "48:5a:3f:7f:e7:9d"}


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

@ask.intent('PlayRadioIntent', mapping={'state': 'state'})
def play_radio(state):
    if state in ['on', 'listen']:
        os.system('%s %s %s'% (audioplayer, stationLink, options_))
        return statement('Now playing internet radio.')
    if state in ['off', 'disconnect']:
        os.system('pkill -9 %s'% (audioplayer))
        return statement('Switched off radio.')

@ask.intent('DriveTimeIntent', mapping={'origin': 'origin', 'dest':'dest'})
def getDrivingTime(origin, dest):
    # https://developers.google.com/maps/documentation/javascript/examples/places-placeid-finder
    # origin_id = 'ChIJ8ZAz-GDKzR0RlfMgHD9pu6E'
    # dest_id = 'ChIJ9UegMu9czB0Rr9knXwHdykk'
    # url = 'https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}'.format(
    #    origin, dest, apiKey)

    # GET RESULTS BY PLACE ID
    # https://maps.googleapis.com/maps/api/directions/json?origin=place_id:ChIJ685WIFYViEgRHlHvBbiD5nE&
    # destination=place_id:ChIJA01I-8YVhkgRGJb0fW4UX7Y&key=YOUR_API_KEY
    if origin in ['home', 'somerset west']:
        origin = 'Somerset West, South Africa'
    if origin in ['work', 'ska', 'work']:
        origin = 'SKA South Africa, Pinelands, South Africa'

    if dest in ['home', 'somerset west']:
        dest = 'Somerset West, South Africa'
    if dest in ['work', 'ska', 'work']:
        dest = 'SKA South Africa, Pinelands, South Africa'

    gmaps = googlemaps.Client(key=googlemaps_api)
    now = datetime.now()

    try:
        rawDirection = gmaps.directions(origin, dest, departure_time=now)[0]
    except Exception:
        return statement('Could not get the actual time and distance of your commute')
    else:
        legs = rawDirection['legs'][0]
        distance = legs['distance']['text']
        duration = legs['duration']['text']
        start_address = legs['start_address']
        end_address = legs['end_address']
        msg = ('Your commute will take you approximately %s/%s travelling from %s to %s.'%(duration,
                                                                                           distance,
                                                                                           start_address,
                                                                                           end_address))
        return statement(msg)

@ask.intent('GetNewsIntent')
def getNews():
    try:
        rss = feedparser.parse(rssfeed)
    except rss.bozo, errmsg:
        return statement('Failed to retrieve news from News24: reason: %s' % errmsg)
    else:
        msg = ' '.join([rss.entries[i]['description'] for i in range(headlinesCount)]))
        try:
            msg = msg.encode('ascii', 'ignore').decode('ascii')
        except:
            msg = msg.encode('ascii', 'ignore')
        return statement(msg + '. That is all for now.')



def WhosHome():
    def macToIP(macAddress):
        count = 0
        timeout = 10
        while True:
            process = subprocess.Popen(
                'timeout {} sudo arp-scan -l | grep {} | cut -f 1'.format(timeout, macAddress),
                shell=True, stdout=subprocess.PIPE, )
            mob_ip = process.communicate()[0].strip()
            if mob_ip != '':
                return mob_ip
            if count > 2:
                return '10.10.10.10'
            time.sleep(.01)
            count += 1

    def getipAdresses(macAddress):
        ipAddresses = []
        for i, v in macAddress.items():
            ipAddresses.append(macToIP(v))
        return ipAddresses

    macAddress = presenceDetect#{k: v for k, v in configFile()['presenceDetect'].items() if v != 'None'}
    useripMap = dict(zip(macAddress.keys(), getipAdresses(macAddress)))

    class Pinger(object):
        status = {'Home': [], 'Not Home': []}
        hosts = []
        # How many ping process at the time.
        thread_count = 4
        lock = threading.Lock()

        def ping(self, ip):
            # Use the system ping command with count of 1 and wait time of 1.
            ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
                                  stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
            return ret == 0  # Return True if our ping command succeeds

        def pop_queue(self):
            ip = None
            self.lock.acquire()
            if self.hosts:
                ip = self.hosts.pop()
            self.lock.release()
            return ip

        def dequeue(self):
            while True:
                ip = self.pop_queue()
                if not ip:
                    return None
                result = 'Home' if self.ping(ip) else 'Not Home'
                self.status[result].append(ip)

        def start(self):
            threads = []
            for i in range(self.thread_count):
                t = threading.Thread(target=self.dequeue)
                t.start()
                threads.append(t)

            [t.join() for t in threads]
            return self.status

    def PingStatus(ipAddressList):
        PresenseDetect = Pinger()
        PresenseDetect.thread_count = 8
        PresenseDetect.hosts = ipAddressList
        status = PresenseDetect.start()
        return set(status['Home'])

    isHome = list(PingStatus(useripMap.values()))
    whosHome = [b for i in isHome for b, a in useripMap.items() if a == i]
    return whosHome



if __name__ == '__main__':

    port = 5050
    app.run(host='0.0.0.0', port=port)
