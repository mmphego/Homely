import sys
import time
import random
import datetime
import telepot
import LowLevel

from cleverbot import Cleverbot

chatbot = Cleverbot('chatbot')
telegramAPI = '259841183:AAGRjAK_nGepqLQEJn4N-YIpO6nsPlAypRE'
conf = LowLevel.configFile

username = conf['username']
Persons_ = [str(y) for x, y in {k: v for k, v in conf['allowedPersons'].items() if v != 'None'}.items()]
AllowedPersons = set(Persons_)


origin = LowLevel.origin
dest = LowLevel.dest


HelpMessage = ("Acceptable commands\n"
               "\n"
               "    * /temperature or /temp: Get current temperature, humidity and luminousity.\n"
               "    * /weather: Get current weather forecast in your area.\n"
               "    * /ip: Get current systems IP.\n"
               "    * /tts_on or /tts_off: Enable or Disable test to speech\n"
               "\n"
               "    * /home? or /whos_home: Find out who is home, usually takes few seconds to process?\n"
               "    * /news: Gets the current news from News24\n"
               "\n"
               "    * /time_to_work: Get commute time from home to work\n"
               "    * /time_to_home: Get commute time from work to home\n"
               #"\n"
               #"    * /light x on / ledx on / switch light x on - Switches light x on , Where x is a 1-4\n"
               #"    * /light x off / ledx off / switch light x off - Switches light x off. Where x is a 1-4\n"
               "\n"
               "    * /server_on or /server_off: Switch media server on or off\n\n\n"
               "    Or we can chat!\n"
               "    ")

def PossibleStrings(msg):
    return [msg.upper(), msg.lower(), msg.title(), msg.capitalize(), msg.swapcase()]

def handler(msg):
    username = msg['from']['username']
    chat_id = msg['chat']['id']
    revdMsg = msg['text']
    if username in PossibleStrings('mmphego') or PossibleStrings('mpho'):
        if revdMsg == '/help':
            bot.sendMessage(chat_id, HelpMessage)

        elif revdMsg == '/weather':
            weather = LowLevel.getWeather()
            bot.sendMessage(chat_id, weather)

        elif revdMsg == '/ip':
            ip = LowLevel.getIP()
            bot.sendMessage(chat_id, ip)

        elif revdMsg in ['/home', '/whos_home']:
            whos_home = LowLevel.WhosHome()
            bot.sendMessage(chat_id, whos_home)

        elif revdMsg == '/time_to_work':
            time_to_work = LowLevel.getDrivingTime(dest, origin)
            bot.sendMessage(chat_id, time_to_work)

        elif revdMsg == '/time_to_home':
            time_to_home = LowLevel.getDrivingTime(origin, dest)
            bot.sendMessage(chat_id, time_to_home)

        elif revdMsg == '/news':
            weather = LowLevel.getNews()
            bot.sendMessage(chat_id, weather)
        else:
            bot.sendMessage(chat_id, chatbot.ask(revdMsg))
    else:
        bot.sendMessage(chat_id, 'who the fuck are you?')


bot = telepot.Bot(telegramAPI)
bot.message_loop(handler)
print 'Listening...'
while True:time.sleep(10)
