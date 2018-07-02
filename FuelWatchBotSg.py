# fuelWatchBotSG *Work in progress
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A Simple way to send a message to telegram
import telegram
from telegram import MessageEntity, TelegramObject, ChatAction, Location, ReplyKeyboardMarkup, ReplyKeyboardRemove
import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler

from pprint import pprint
from functools import wraps
from future.builtins import bytes
from pymongo import MongoClient
from pathlib import Path
import numpy as np
import argparse
import logging
import sys
import json
import random
import datetime
from dateutil.relativedelta import relativedelta
import re 
import os
import sys
import yaml
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image

# For plotting messages / price charts
#import pandas as pd 

import requests

PATH = os.path.dirname(os.path.abspath(__file__))

"""
# Configure Logging
"""
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info("Running "+sys.argv[0])

"""
#	Load the config file
#	Set the Botname / Token
"""
config_file = PATH+'/config.yaml'
my_file     = Path(config_file)
if my_file.is_file():
    with open(config_file) as fp:
        config = yaml.load(fp)
else:
    pprint('config.yaml file does not exists. Please make from config.sample.yaml file')
    sys.exit()


BOTNAME                     = config['FUELWATCHSG_BOT_USERNAME']
TELEGRAM_BOT_TOKEN          = config['FUELWATCHSG_BOT_TOKEN']
FORWARD_PRIVATE_MESSAGES_TO = config['BOT_OWNER_ID'] 
ADMINS                      = config['ADMINS']


MESSAGES = {}
MESSAGES['welcome']         = config['MESSAGES']['welcome']
MESSAGES['welcomewomen']    = config['MESSAGES']['welcome_special']
MESSAGES['goodbye']         = config['MESSAGES']['goodbye']
MESSAGES['pmme']            = config['MESSAGES']['pmme']
MESSAGES['start']           = config['MESSAGES']['start']
MESSAGES['admin_start']     = config['MESSAGES']['admin_start']
MESSAGES['about']           = config['MESSAGES']['about']
MESSAGES['price']           = config['MESSAGES']['price']
MESSAGES['comment']         = config['MESSAGES']['comment']
MESSAGES['location']        = config['MESSAGES']['location']

MESSAGES['nearest']           = config['MESSAGES']['nearest']
MESSAGES['nearestspc']           = config['MESSAGES']['nearestspc']
MESSAGES['nearestshell']         = config['MESSAGES']['nearestshell']
MESSAGES['nearestcal']        = config['MESSAGES']['nearestcal']

ADMINS_JSON                 = config['MESSAGES']['admins_json']

#################################
# Begin bot.. 

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Bot error handler
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

# Restrict bot functions to admins
def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


#################################
#			UTILS	

# Resolve message data to a readable name 	 		
def get_name(user):
    try:
        name = user.first_name
    except (NameError, AttributeError):
        try:
            name = user.username
        except (NameError, AttributeError):
            logger.info("No username or first name.. wtf")
            return	""
    return name



#################################
#		BEGIN BOT COMMANDS 		

# Returns the user their user id 
def getid(bot, update):
    pprint(update.message.chat.__dict__, indent=4)
    update.message.reply_text(str(update.message.chat.first_name)+" :: "+str(update.message.chat.id))

#URL = "https://storage.scrapinghub.com/items/324456/1/2/0?apikey=19b8c3bd229f43d9bc1c19f2b1f9074e&format=json"
URL = "https://storage.scrapinghub.com/items/324456/2/3/0?apikey=19b8c3bd229f43d9bc1c19f2b1f9074e&format=json"

def get_url(url):
    response = requests.get(url)
    content = {}
    content = response.content.decode("utf8")
    print (content)
    js = json.loads(content)
    return js

# Welcome message 
def start(bot, update):

    user_id = update.message.from_user.id 
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    user_id = update.message.from_user.id 
    name = get_name(update.message.from_user)
    logger.info("/start - "+name)

    pprint(update.message.chat.type)

    if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
    	msg = random.choice(MESSAGES['pmme']) % (name)
    	bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
    else:
        msg = MESSAGES['welcome']

        timestamp = datetime.datetime.utcnow()
        info = { 'user_id': user_id, 'request': 'start', 'timestamp': timestamp }
	#db.pm_requests.insert(info)
        msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['start'] % name),parse_mode="Markdown",disable_web_page_preview=1)            
        if user_id in ADMINS:
            msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['admin_start'] % name),parse_mode="Markdown",disable_web_page_preview=1)


def about(bot, update):

    user_id = update.message.from_user.id 
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    name = get_name(update.message.from_user)
    logger.info("/about - "+name)

    if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
    	msg = random.choice(MESSAGES['pmme']) % (name)
    	bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
    else:
    	msg = MESSAGES['about']
    	timestamp = datetime.datetime.utcnow()
    	info = { 'user_id': user_id, 'request': 'about', 'timestamp': timestamp }
    	#db.pm_requests.insert(info)
    	bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def price(bot, update):

    user_id = update.message.from_user.id 
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    name = get_name(update.message.from_user)
    logger.info("/price - "+name)
    
    msg = MESSAGES['price']
    timestamp = datetime.datetime.utcnow()
	
    info = { 'user_id': user_id, 'request': 'price', 'timestamp': timestamp }
    #db.pm_requests.insert(info)
	
    bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1)
    ScrapData_JSON = get_url(URL)
    msg = " price of 95 = $1.76"
    '''
    keys = list(ScrapData_JSON.keys())
    random.shuffle(keys)
    for k in keys: 
        msg += ""+k+"\n"
        msg += ADMINS_JSON[k]['Platinum 98 with Tehcron']+"\n"
        msg += "_"+ADMINS_JSON[k]['Premium 95 with Techronabout']+"_"
        msg += "\n\n"
	sg += "/start - to go back to home"
        '''
    print ("/n/n/n/n/n/n/")
    bot.sendMessage(chat_id=chat_id,text=(msg),parse_mode="Markdown",disable_web_page_preview=1) 


def admins(bot, update):

    user_id = update.message.from_user.id 
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    name = get_name(update.message.from_user)
    logger.info("/admins - "+name)

    if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
            msg = random.choice(MESSAGES['pmme']) % (name)
            bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
    else:
            msg = "*Whalepool Admins*\n\n"
            keys = list(ADMINS_JSON.keys())
            random.shuffle(keys)
            for k in keys: 
                    msg += ""+k+"\n"
                    msg += ADMINS_JSON[k]['adminOf']+"\n"
                    msg += "_"+ADMINS_JSON[k]['about']+"_"
                    msg += "\n\n"
            msg += "/start - to go back to home"

            timestamp = datetime.datetime.utcnow()
            info = { 'user_id': user_id, 'request': 'admins', 'timestamp': timestamp }
            #db.pm_requests.insert(info)

            bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

def comment(bot, update):

    user_id = update.message.from_user.id 
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    name = get_name(update.message.from_user)
    logger.info("/comment - "+name)

    if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
            msg = random.choice(MESSAGES['pmme']) % (name)
            bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
    else:
            msg = MESSAGES['comment']

            timestamp = datetime.datetime.utcnow()
            info = { 'user_id': user_id, 'request': 'comment', 'timestamp': timestamp }
            #db.pm_requests.insert(info)

            #bot.sendSticker(chat_id=chat_id, sticker="CAADBAADqgIAAndCvAiTIPeFFHKWJQI", disable_notification=False)
            bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


def location_checker(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    name = get_name(update.message.from_user)
    logger.info("/User_Location - "+name)
    
    if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
            msg = random.choice(MESSAGES['pmme']) % (name)
            bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
    else:
            msg = MESSAGES['location']
            
            timestamp = datetime.datetime.utcnow()
            info = { 'user_id': user_id, 'request': 'location', 'timestamp': timestamp }
            #db.pm_requests.insert(info)
            user = update.message.from_user
            user_location = update.message.location
            user = update.message.from_user
            user_location = update.message.location
            print (user_location)
            if user_location != None:
                logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,user_location.longitude)
                #update.message.reply_text('Thank you for updating your location! If the location is wrong, please send the location again. Thank you!')
                reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
                bot.send_message(chat_id=chat_id,text="Thank you for updating your location! If the location is wrong, please send the location again. Thank you!",reply_markup=reply_markup)
                ## send back users location
                bot.send_location(user_id,user_location.latitude,user_location.longitude)
            else:
                print ("  ")
                location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
                contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
                custom_keyboard = [[ location_keyboard]]
                reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                bot.send_message(chat_id=chat_id,text="Would you mind sharing your location and contact with me?",reply_markup=reply_markup)
            

def nearest(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    name = get_name(update.message.from_user)
    logger.info("/nearest - "+name)
    
    if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
            msg = random.choice(MESSAGES['pmme']) % (name)
            bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
    else:
            msg = MESSAGES['nearest']
            timestamp = datetime.datetime.utcnow()
            info = { 'user_id': user_id, 'request': 'nearest', 'timestamp': timestamp }
            #db.pm_requests.insert(info)
            user = update.message.from_user
            user_location = update.message.location
            user = update.message.from_user
            user_location = update.message.location
            print (user_location)
            '''
            if user_location != None:
                logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,user_location.longitude)
                #update.message.reply_text('Thank you for updating your location! If the location is wrong, please send the location again. Thank you!')
                reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
                bot.send_message(chat_id=chat_id,text="Thank you for updating your location! If the location is wrong, please send the location again. Thank you!",reply_markup=reply_markup)
                ## send back users location
                bot.send_location(user_id,user_location.latitude,user_location.longitude)
            else:
                location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
                contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
                custom_keyboard = [[ location_keyboard]]
                reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                bot.send_message(chat_id=chat_id,text="Would you mind sharing your location and contact with me?",reply_markup=reply_markup)
                '''
            msg = MESSAGES['nearest']
            bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

####################################################
# ADMIN FUNCTIONS
@restricted
def liststations(bot,update):

    chat_id = update.message.chat.id

    pipe = [ { "$group": { "_id": "$file_id", "total": { "$sum": 1 }  } }, { "$sort": { "total": -1 } }, { "$limit": 5 }   ]
    gifs = list(db.natalia_gifs.aggregate(pipe))

    bot.sendMessage(chat_id=WP_ROOM, text="Whalepool most popular gif ever with "+str(gifs[0]['total'])+" posts is..." )
    bot.sendSticker(chat_id=WP_ROOM, sticker=gifs[0]['_id'], disable_notification=False)
    bot.sendMessage(chat_id=chat_id, text="message has been posted to "+ROOM_ID_TO_NAME[WP_ROOM] )

@restricted
def listadmin(bot,update):

    chat_id = update.message.chat.id

    pipe = [ { "$group": { "_id": "$file_id", "total": { "$sum": 1 }  } }, { "$sort": { "total": -1 } }, { "$limit": 5 }   ]
    gifs = list(db.natalia_gifs.aggregate(pipe))

    bot.sendMessage(chat_id=WP_ROOM, text="Whalepool most popular gif ever with "+str(gifs[0]['total'])+" posts is..." )
    bot.sendSticker(chat_id=WP_ROOM, sticker=gifs[0]['_id'], disable_notification=False)
    bot.sendMessage(chat_id=chat_id, text="message has been posted to "+ROOM_ID_TO_NAME[WP_ROOM] )


@restricted
def getlog(bot,update):

    chat_id = update.message.chat.id

    pipe = [ { "$group": { "_id": "$file_id", "total": { "$sum": 1 }  } }, { "$sort": { "total": -1 } }, { "$limit": 5 }   ]
    gifs = list(db.natalia_gifs.aggregate(pipe))

    bot.sendMessage(chat_id=WP_ROOM, text="Whalepool most popular gif ever with "+str(gifs[0]['total'])+" posts is..." )
    bot.sendSticker(chat_id=WP_ROOM, sticker=gifs[0]['_id'], disable_notification=False)
    bot.sendMessage(chat_id=chat_id, text="message has been posted to "+ROOM_ID_TO_NAME[WP_ROOM] )

@restricted
def todaysusers(bot, update):

    chat_id = update.message.chat.id

    bot.sendMessage(chat_id=chat_id, text="Okay gimme a second for this one.. it takes some resources.." )
    logger.info("Today in words..")
    logger.info("Fetching from db...")

    start = datetime.datetime.today().replace(hour=0,minute=0,second=0)
    pipe  = { '_id': 0, 'message': 1 }
    msgs  = list(db.natalia_textmessages.find({ 'timestamp': {'$gt': start } }, pipe ))

    usernames = []
    for w in msgs:
            results = re.findall(r"(.*(?=:)): (.*)", w['message'])[0]
            usernames.append(results[0].strip())

    extra_stopwords = EXTRA_STOPWORDS
    for e in extra_stopwords:
            STOPWORDS.add(e)

    stopwords = set(STOPWORDS)

    logger.info("Building usernames pic...")
    PATH_MASK      = PATH+"media/wp_background_mask2.png"
    PATH_BG        = PATH+"media/wp_background.png"
    PATH_USERNAMES = PATH+"telegram-usernames.png"

    # Usernames
    d = os.path.dirname('__file__')

    mask = np.array(Image.open(PATH_MASK))

    wc = WordCloud(background_color=None, max_words=2000,mask=mask,colormap='BuPu',
                   stopwords=stopwords,mode="RGBA", width=800, height=400)
    wc.generate(' '.join(usernames))
    wc.to_file(PATH_USERNAMES)

    layer1 = Image.open(PATH_BG).convert("RGBA")
    layer2 = Image.open(PATH_USERNAMES).convert("RGBA")

    Image.alpha_composite(layer1, layer2).save(PATH_USERNAMES)

    msg = bot.sendPhoto(chat_id=WP_ROOM, photo=open("telegram-usernames.png",'rb'), caption="Todays Users" )
    bot.sendMessage(chat_id=chat_id, text="Posted today in pictures to "+ROOM_ID_TO_NAME[WP_ROOM] )

    os.remove(PATH_USERNAMES)


@restricted 
def promotets(bot, update):

    pprint('promotets...')

    chat_id = update.message.chat_id
    name = get_name(update.message.from_user)
    fmsg = re.findall( r"\"(.*?)\"", update.message.text)

    if len(fmsg) > 0:

        # rooms = [WP_ROOM]
        rooms = [WP_ROOM, SP_ROOM, MH_ROOM, WP_FEED, SP_FEED]

        for r in rooms:

            message = fmsg[0]
            bot.sendSticker(chat_id=r, sticker="CAADBAADcwIAAndCvAgUN488HGNlggI", disable_notification=False)
            msg = bot.sendMessage(chat_id=r, parse_mode="Markdown", text=fmsg[0]+"\n-------------------\n*/announcement from "+name+"*" )


            if r in [WP_ROOM, SP_ROOM, MH_ROOM]: 
                bot.pin_chat_message(r, msg.message_id, disable_notification=True)

            bot.sendMessage(chat_id=r, parse_mode="Markdown", text="Message me ("+BOTNAME.replace('_','\_')+") - to see details on how to connect to [teamspeak](https://whalepool.io/connect/teamspeak) also listen in to the listream here: livestream.whalepool.io", disable_web_page_preview=True )
            bot.sendMessage(chat_id=chat_id, parse_mode="Markdown", text="Broadcast sent to "+ROOM_ID_TO_NAME[r])

                

    else:
        bot.sendMessage(chat_id=chat_id, text="Please incldue a message in quotes to spam/shill the teamspeak message" )	


@restricted
def commandstats(bot, update):
    chat_id = update.message.chat_id
    start = datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0)
    # start = start - relativedelta(days=30)

    pipe = [ 
            { "$match": { 'timestamp': {'$gt': start } } }, 
            { "$group": { 
                    "_id": { 
                            "year" : { "$year" : "$timestamp" },        
                            "month" : { "$month" : "$timestamp" },        
                            "day" : { "$dayOfMonth" : "$timestamp" },
                            "request": "$request"
                    },
                    "total": { "$sum": 1 }  
                    } 
            }, 
            { "$sort": { "total": -1  } }, 
            # { "$limit": 3 }   
    ]
    res = list(db.pm_requests.aggregate(pipe))

    output = {}
    totals = {}

    for r in res: 

        key = r['_id']['day']
        if not(key in output):
                output[key] = {}

        request = r['_id']['request']
        if not(request in output[key]):
                output[key][r['_id']['request']] = 0 

        if not(request in totals):
                totals[request] = 0

        output[key][r['_id']['request']] += r['total']
        totals[request] += r['total']


    reply = "*Natalia requests since the start of the month...*\n"
    for day in sorted(output.keys()):
        reply += "--------------------\n"
        reply += "*"+str(day)+"*\n"

        for request, count in output[day].items():
                reply += request+" - "+str(count)+"\n"

                
    reply += "--------------------\n"
    reply += "*Totals*\n"
    for request in totals:
        reply += request+" - "+str(totals[request])+"\n"


    bot.sendMessage(chat_id=chat_id, text=reply, parse_mode="Markdown" )

@restricted
def locationstats(bot, update):
    chat_id = update.message.chat_id
    start = datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0)
    # start = start - relativedelta(days=30)

    pipe = [ 
            { "$match": { 'timestamp': {'$gt': start } } }, 
            { "$group": { 
                    "_id": { 
                            "year" : { "$year" : "$timestamp" },        
                            "month" : { "$month" : "$timestamp" },        
                            "day" : { "$dayOfMonth" : "$timestamp" },
                            "request": "$request"
                    },
                    "total": { "$sum": 1 }  
                    } 
            }, 
            { "$sort": { "total": -1  } }, 
            # { "$limit": 3 }   
    ]
    res = list(db.pm_requests.aggregate(pipe))

    output = {}
    totals = {}

    for r in res: 

        key = r['_id']['day']
        if not(key in output):
                output[key] = {}

        request = r['_id']['request']
        if not(request in output[key]):
                output[key][r['_id']['request']] = 0 

        if not(request in totals):
                totals[request] = 0

        output[key][r['_id']['request']] += r['total']
        totals[request] += r['total']


    reply = "*Natalia requests since the start of the month...*\n"
    for day in sorted(output.keys()):
        reply += "--------------------\n"
        reply += "*"+str(day)+"*\n"

        for request, count in output[day].items():
                reply += request+" - "+str(count)+"\n"

                
    reply += "--------------------\n"
    reply += "*Totals*\n"
    for request in totals:
        reply += request+" - "+str(totals[request])+"\n"


    bot.sendMessage(chat_id=chat_id, text=reply, parse_mode="Markdown" )


@restricted 
def joinstats(bot,update):

    chat_id = update.message.chat_id
    start = datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0)
    # start = start - relativedelta(days=30)

    pipe = [ 
            { "$match": { 'timestamp': {'$gt': start } } }, 
            { "$group": { 
                    "_id": {     
                            "day" : { "$dayOfMonth" : "$timestamp" },
                            "chat_id": "$chat_id"
                    },
                    "total": { "$sum": 1 }  
                    } 
            }, 
            { "$sort": { "total": -1  } }, 
            # { "$limit": 3 }   
    ]
    res = list(db.room_joins.aggregate(pipe))

    output = {}
    totals = {}

    for r in res: 

        key = r['_id']['day']
        if not(key in output):
                output[key] = {}

        roomid = r['_id']['chat_id']
        if not(roomid in output[key]):
                output[key][roomid] = 0 

        if not(roomid in totals):
                totals[roomid] = 0

        output[key][roomid] += r['total']
        totals[roomid] += r['total']



    reply = "*Channel Joins since the start of the month...*\n"
    for day in sorted(output.keys()):
        reply += "--------------------\n"
        reply += "*"+str(day)+"*\n"

        for room, count in output[day].items():
            reply += ROOM_ID_TO_NAME[room]+" - "+str(count)+"\n"


    reply += "--------------------\n"
    reply += "*Totals*\n"
    for roomid in totals:
        reply += ROOM_ID_TO_NAME[roomid]+" - "+str(totals[roomid])+"\n"


    bot.sendMessage(chat_id=chat_id, text=reply, parse_mode="Markdown" )

#################### End of Admin commands
	
# Just log/handle a normal message
def log_message_private(bot, update):
#	pprint(update.__dict__, indent=4)
    # pprint(update.message.__dict__, indent=4)
    username = update.message.from_user.username 
    user_id = update.message.from_user.id 
    message_id = update.message.message_id 
    chat_id = update.message.chat.id
    name = get_name(update.message.from_user)

    logger.info("Private Log Message: "+name+" said: "+update.message.text)

    # msg = bot.forwardMessage(chat_id=FORWARD_PRIVATE_MESSAGES_TO, from_chat_id=chat_id, message_id=message_id)

    msg = bot.sendMessage(chat_id=chat_id, text=(MESSAGES['start'] % name),parse_mode="Markdown",disable_web_page_preview=1)


#################################
# Command Handlers
logger.info("Setting  command handlers")
updater = Updater(bot=bot,workers=10)
dp      = updater.dispatcher

#User Commands
dp.add_handler(CommandHandler('id', getid))
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('about', about))
dp.add_handler(CommandHandler('admins', admins))
dp.add_handler(CommandHandler('location', location_checker))
dp.add_handler(CommandHandler('price', price))
dp.add_handler(CommandHandler('comment', comment))
#functions that need to be added
dp.add_handler(CommandHandler('nearest', nearest))
dp.add_handler(CommandHandler('nearestspc', nearest))
dp.add_handler(CommandHandler('nearestshell', nearest))
dp.add_handler(CommandHandler('nearestcal', nearest))

#Admin Commands
dp.add_handler(CommandHandler('commandstats',commandstats))
dp.add_handler(CommandHandler('locationstats',locationstats))
dp.add_handler(CommandHandler('joinstats',joinstats))
dp.add_handler(CommandHandler('liststations', liststations))
dp.add_handler(CommandHandler('listadmin', listadmin))
dp.add_handler(CommandHandler('getlog', getlog))
dp.add_handler(CommandHandler('todaysusers', todaysusers))
dp.add_handler(CommandHandler('promotets', promotets))

# Location message
dp.add_handler(MessageHandler(Filters.location, location_checker))

# Photo message
#dp.add_handler(MessageHandler(Filters.photo, photo_message))

# Sticker message
#dp.add_handler(MessageHandler(Filters.sticker, sticker_message))

# Normal Text chat
#dp.add_handler(MessageHandler(Filters.text, echo))


# log all errors
dp.add_error_handler(error)



#################################
# Polling 
logger.info("Starting polling")
updater.start_polling()


# PikaWrapper()

