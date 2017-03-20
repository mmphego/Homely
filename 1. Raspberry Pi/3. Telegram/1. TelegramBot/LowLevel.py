import feedparser
import json
import os
#import pygame
import subprocess
import threading
import time
import urllib2
import googlemaps
import yaml

from datetime import datetime
from gtts import gTTS
from getpass import getuser

rssfeed = 'http://feeds.news24.com/articles/News24/SouthAfrica/rss'
headlinesCount = 5

username = getuser()

def configFile():
    if 'CONFIGFILE' in os.environ.keys():
        config_link = os.environ['CONFIGFILE']
        if os.path.isfile(config_link):
            with open(config_link) as ymlfile:
                cfg = yaml.load(ymlfile)
            return cfg
    else:
        config_link = '/home/%s/config/config.yaml'% username
        if os.path.isfile(config_link):
            with open(config_link) as ymlfile:
                cfg = yaml.load(ymlfile)
            return cfg

configFile = configFile()
enableTTS = configFile['enableTTS']
debugEnabled = configFile['debugEnabled']
googlemaps_api = configFile['googlemaps_api']
origin = configFile['origin_address']
dest = configFile['dest_address']
openWeatherAPI = configFile['APIs']['openWeatherAPI']


def getTemp():
    result = float(subprocess.check_output(
        ["/opt/vc/bin/vcgencmd measure_temp | cut -c6-9"], shell=True)[: -1])
    return ("My current temperature is %s C" % str(result))

def getIP():
    result = subprocess.check_output("hostname -I", shell=True)
    return ('My current IP is %s' % str(result))

def rebootPi():
    subprocess.check_output("sudo reboot", shell=True)

def getUptime():
    result = subprocess.check_output("uptime", shell=True)
    return ('Current uptime: %s' % str(result))

def getDistStatus():
    result = subprocess.check_output("df -h | grep G", shell=True)
    return ('Current Disk Usage:\n\t %s' % str(result))

def getWeather():
    # get current city using geo ip location
    geoip = urllib2.Request('http://ip-api.com/json')
    geoip_read = json.loads(urllib2.urlopen(geoip).read())
    if geoip_read['status'] == 'success':
        geoip_city = str(geoip_read['city'])
        geoip_country = str(geoip_read['countryCode'])
        geoip_zip = str(geoip_read['zip'])
        # if geoip_country == 'ZA': geoip_country = 'SA'
        geoip_coord = (geoip_read['lon'],
                       geoip_read['lat'])
    else:
        geoip_config = configFile()['geography']
        geoip_city = geoip_config['city']
        geoip_country = geoip_config['country']
        geoip_zip = geoip_config['code']
        geoip_coord = geoip_config['coord'].split(',')

    # Get todays weather
    request = ('http://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}'.format(
        geoip_city.replace(' ', '').lower(), geoip_country, openWeatherAPI))

    # request = urllib2.Request('http://api.openweathermap.org/data/2.5/'
    #    'weather?q={},{}&units=metric'.format(geoip_city, geoip_country))

    # Get forecast
    request_2 = ('http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&cnt=1&units='
                 'metric&appid={}'.format(geoip_coord[1], geoip_coord[0], openWeatherAPI))

    # except Exception:
    # request = urllib2.Request('http://api.openweathermap.org/data/2.5/'
    # 'weather?q=pretoria&units=metric')
    # request_2 = urllib2.Request('http://api.openweathermap.org/data/2.5/'
    # 'forecast?lat=18.4&lon=-33.9833&cnt=1&units=metric')


    weather_api = urllib2.urlopen(request)
    response = weather_api.read()
    response_dictionary = json.loads(response)
    weather_api.close()
    forecast_api = urllib2.urlopen(request_2)
    response_2 = forecast_api.read()
    response_2_dictionary = json.loads(response_2)
    forecast_api.close()

    try:
        current = response_dictionary['main']['temp'] / 10.
        current_low = response_dictionary['main']['temp_min']
        if current_low > 50:
            current_low = current_low / 10.
        current_high = response_dictionary['main']['temp_max']
        if current_high > 50:
            current_high = current_high / 10.
        conditions = response_dictionary['weather'][0]['description']
    except KeyError:
        raise RuntimeError('Unable to read links')

    current = str(round(current, 1))
    current_low = str(round(current_low, 1))
    current_high = str(round(current_high, 1))
    todays_low = response_2_dictionary['list'][0]['main']['temp_min']
    todays_high = response_2_dictionary['list'][0]['main']['temp_max']

    todays_low_str = str(round(todays_low, 1))
    todays_high_str = str(round(todays_high, 1))

    wtr = ('Weather conditions for today, %s with a current temperature of %s C, a low of %s C and '
           'a high of %s C' % (conditions, current, todays_low_str, todays_high_str))
    return wtr

def getNews():
    global rssfeed, headlinesCount
    try:
        rss = feedparser.parse(rssfeed)
    except rss.bozo, errmsg:
        return 'Failed to reach News24: reason: %s' % errmsg
    else:
        newsfeed = '\n\n'.join([rss.entries[i]['description'] for i in range(headlinesCount)])
        return newsfeed.encode("ascii", "ignore").decode('ascii')

def Speak(words):
    mp3Playr = '/usr/bin/mpg123 -q'
    filename = '/tmp/talk.mp3'
    try:
        tts = gTTS(text=words, lang='en-au')
        tts.save('{}'.format(filename))
    except:
        pass
        # subprocess.check_output('echo {} | festival --tts'.format(words), shell=True)
        # Play the mp3s returned
    else:
    #    subprocess.call('{} {}'.format(mp3Playr, filename), shell=True)
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True: continue

def getDrivingTime(origin, dest):
    # https://developers.google.com/maps/documentation/javascript/examples/places-placeid-finder
    # origin_id = 'ChIJ8ZAz-GDKzR0RlfMgHD9pu6E'
    # dest_id = 'ChIJ9UegMu9czB0Rr9knXwHdykk'
    # url = 'https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}'.format(
    #    origin, dest, apiKey)

    # GET RESULTS BY PLACE ID
    # https://maps.googleapis.com/maps/api/directions/json?origin=place_id:ChIJ685WIFYViEgRHlHvBbiD5nE&
    # destination=place_id:ChIJA01I-8YVhkgRGJb0fW4UX7Y&key=YOUR_API_KEY
    gmaps = googlemaps.Client(key=googlemaps_api)
    now = datetime.now()

    try:
        rawDirection = gmaps.directions(origin, dest, departure_time=now)[0]
    except Exception:
        return 'Could not get the actual time and distance of your commute'
    else:
        legs = rawDirection['legs'][0]
        distance = legs['distance']['text']
        duration = legs['duration_in_traffic']['text']
        start_address = legs['start_address']
        end_address = legs['end_address']
        msg = ('Your commute will take you approximately {}/{} travelling from {} \nto {}.'
               .format(duration, distance, start_address, end_address))
        return msg

def WhosHome():
    def macToIP(macAddress):
        count = 0
        timeout = 10
        while True:
            process = subprocess.Popen(
                'timeout {} sudo arp-scan -l | grep {} | cut -f 1'.format(timeout,
                                                                                            macAddress),
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

    macAddress = {k: v for k, v in configFile()['presenceDetect'].items() if v != 'None'}
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


# class GPIOControl(object):
#     def __init__(self, wiringpi, relayDict):
#         self.wiringpi = wiringpi
#         self.relays = relayDict

#     def updateRelays(self):
# #        locals().update(self.relays)
#         for relay, gpio in self.relays.iteritems():
#             subprocess.check_call([self.wiringpi, 'mode', '{}'.format(gpio), 'out'])
#             if debugEnabled:
#                 print 'Setting {} pin {} to be output'.format(relay, gpio)

#     def relay_off(self, pin):
#         subprocess.check_call([self.wiringpi, 'write', '{}'.format(pin), '0'])

#     def relay_on(self, pin):
#         subprocess.check_call([self.wiringpi, 'write', '{}'.format(pin), '1'])


# wiringpi = '/usr/local/bin/gpio'
# relayDict = configFile()['RelaysSetup']
# RelayControl = GPIOControl(wiringpi, relayDict)
# RelayControl.updateRelays()
