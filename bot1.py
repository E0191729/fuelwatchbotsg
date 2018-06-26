import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop

import urllib
from io import BytesIO
from PIL import Image

"""
After **inserting token** in the source code, run it:
```
$ python2.7 diceyclock.py
```
[Here is a tutorial](http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/)
teaching you how to setup a bot on Raspberry Pi. This simple bot does nothing
but accepts two commands:
- `/roll` - reply with a random integer between 1 and 6, like rolling a dice.
- `/time` - reply with the current time, like a clock.
"""

url='http://www.emtech.in/wp-content/uploads/2017/03/pic.jpg'


def handle(msg):
    print(msg)
    chat_id = msg['chat']['id']
    print(chat_id)
    command = msg['text']
    

    print ('Got command: %s' % command)

    if command == '/roll':
        bot.sendMessage(chat_id, random.randint(1,6))
    elif command == '/hi':
        bot.sendMessage(chat_id, "hello " + msg['from']['username']+" :)")
    elif command == '/fuel':
        bot.sendMessage(chat_id, "we can print the list of Fuel price here :)")
    elif command == '/deal':
        bot.sendMessage(chat_id, "We can print the list of Deals avilable ;)")
    elif command == '/location':
        bot.sendMessage(chat_id, "This will request for users GeoLocation")
    elif command == '/time':
        bot.sendMessage(chat_id, str(datetime.datetime.now()))
    elif command == '/table':
        bot.sendMessage(chat_id, "This is just an example of a table:")
        bot.sendMessage(chat_id, "Tab 00 \t Tab 01 \t Tab 02 \n List 10 \t List 11 \t List 12 \n List 20 \t List 21 \t List 22")
    elif command == '/pic':
        msgid = msg['message_id']
        '''img = BytesIO(urllib.request.urlopen(url).read())
        bot.send_chat_action(chat_id, 'upload_photo')
        bot.send_photo(chat_id, url, reply_to_message_id=msgid)'''
        photo = open('/home/pi/Desktop/pic.jpg', 'rb')
        bot.sendPhoto(chat_id, photo)
        '''bot.sendPhoto(chat_id, "FILEID")'''

    else:
        bot.sendMessage(chat_id, "Please enter a valid command such as:")
        bot.sendMessage(chat_id, "\n /roll \n /hi \n /fuel \n /deal \n /location \n /time \n /table")

bot = telepot.Bot('')

MessageLoop(bot, handle).run_as_thread()
print ('I am listening ...')

while 1:
    time.sleep(10)
