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
from dateutil.relativedelta import relativedelta
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
from subprocess import call

import numpy as np
import argparse
import logging
import sys
import json
import random
import datetime
import re 
import os
import sys
import yaml
import csv
import requests
import urllib.request
import socket


PATH = os.path.dirname(os.path.abspath(__file__))

"""
# Configure Logging
"""
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info("Running "+sys.argv[0])

"""
# Mongodb 
"""
#client  = MongoClient('mongodb://localhost:27017')
#db      = client.natalia_tg_bot


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
GOOGLE_PLACE_API_KEY		= config['GOOGLE_API_KEY']

config_file = PATH+'/message.yaml'
my_file     = Path(config_file)
if my_file.is_file():
	with open(config_file) as fp:
	    config = yaml.load(fp)
else:
	pprint('message.yaml file does not exists.')
	sys.exit()

price_list = {}
filename = 'run_results_full.csv'
with open(filename, "rt", encoding='utf8') as f:
    reader = csv.reader(f)
    try:
        count = 0
        for row in reader:
            price_list[count] = row
            count =count +1
            print (row)
        msg = "\n"
        for k in range(0, 16):
            msg += price_list[0][k]+" : "
            msg += price_list[1][k] +"\n"
        price_list[3] = msg
        
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

locationHolder = {}
MESSAGES = {}
MESSAGES['welcome']         	= config['MESSAGES']['welcome']
MESSAGES['welcomewomen']    	= config['MESSAGES']['welcome_special']
MESSAGES['goodbye']         	= config['MESSAGES']['goodbye']
MESSAGES['pmme']            	= config['MESSAGES']['pmme']
MESSAGES['start']           	= config['MESSAGES']['start']
MESSAGES['admin_start']     	= config['MESSAGES']['admin_start']
MESSAGES['about']           	= config['MESSAGES']['about']
MESSAGES['price']           	= config['MESSAGES']['price']
MESSAGES['comment']         	= config['MESSAGES']['comment']
MESSAGES['location']        	= config['MESSAGES']['location']

MESSAGES['nearest']           	= config['MESSAGES']['nearest']
MESSAGES['nearestspc']          = config['MESSAGES']['nearestspc']
MESSAGES['nearestshell']        = config['MESSAGES']['nearestshell']
MESSAGES['nearestcal']        	= config['MESSAGES']['nearestcal']
MESSAGES['unknown']		= config['MESSAGES']['unknown']

ADMINS_JSON                 	= config['MESSAGES']['admins_json']

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

def get_url(url):
	response = requests.get(url)
	content = {}
	content = response.content.decode("utf8")
	print (content)
	js = json.loads(content)
	return js
# Local DataBase logger
def log(info):
 	#db = open("/home/dinboy/fuelwatchbotsg-master/localDataBase.txt","a+")
	db = open("/home/pi/fuelwatchbotsg-master/localDataBase.txt","a+")
	db.write("\n" + str(info))
	db.close()
	#db.write(str(info)) #https://www.guru99.com/reading-and-writing-files-in-python.html
	#db.pm_requests.insert(info)

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
	    info = { 'user_name': name ,'user_id': user_id, 'request': 'start', 'timestamp': timestamp }
	    log(info)
	    bot.sendMessage(chat_id=chat_id, text=(MESSAGES['start'] % name),parse_mode="Markdown",disable_web_page_preview=1)            
	    if user_id in ADMINS:
	        bot.sendMessage(chat_id=chat_id, text=(MESSAGES['admin_start'] % name),parse_mode="Markdown",disable_web_page_preview=1)

# Message about the Bot
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
		info = { 'user_name': name ,'user_id': user_id, 'request': 'about', 'timestamp': timestamp }
		log(info)
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

# Bot will reply with the datas from the database
def price(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/price - "+name)
	timestamp = datetime.datetime.utcnow()
	info = { 'user_name': name ,'user_id': user_id, 'request': 'price', 'timestamp': timestamp }
	log(info)
	msg = "*FuelWatchSGBot Price*\n"
	print (price_list[3])
	msg += price_list[3]
	msg += "\n /start - to go back to home"
	bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="HTML",disable_web_page_preview=1)
	#ScrapData_JSON = get_url(URL)
	
	
#info abot the admins
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
	        msg = "*FuelWatchSGBot Admins*\n\n"
	        keys = list(ADMINS_JSON.keys())
	        random.shuffle(keys)
	        for k in keys: 
	                msg += ""+k+"\n"
	                msg += ADMINS_JSON[k]['adminOf']+"\n"
	                msg += "_"+ADMINS_JSON[k]['about']+"_"
	                msg += "\n\n"
	        msg += "/start - to go back to home"

	        timestamp = datetime.datetime.utcnow()
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'admins', 'timestamp': timestamp }
	        log(info)
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
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'comment', 'timestamp': timestamp }
	        log(info)
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
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'location', 'timestamp': timestamp }
	        log(info)
	        user = update.message.from_user
	        user_location = update.message.location
	        user = update.message.from_user
	        user_location = update.message.location
	        print (user_location)
	        if user_location != None:
	            logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,user_location.longitude)
	            reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
	            bot.send_message(chat_id=chat_id,text=msg,reply_markup=reply_markup)
	            ## send back users location
				
	            locationHolder[user_id] = [user_location.latitude , user_location.longitude]
	            print (locationHolder[user_id][0] ,  locationHolder[user_id][1])
	        else:
	            bot.sendMessage(chat_id=chat_id,text="Please share your location to find nearest petrol stations.",parse_mode="Markdown",disable_web_page_preview=1)
	            location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
	            contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
	            custom_keyboard = [[ location_keyboard]]
	            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	            bot.send_message(chat_id=chat_id,text="Would you mind sharing your location with me?",reply_markup=reply_markup)


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
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'nearest', 'timestamp': timestamp }
	        log(info)
	        user = update.message.from_user
	        user_location = update.message.location
	        user = update.message.from_user
	        #print ("#################################### is"+ str(locationHolder[user_id][0]))
	        try:
	        	locationHolder[user_id] == KeyError
	        except KeyError:
	        	user_location = location_checker(bot, update)
	        else:
	        	print (locationHolder[user_id][0] ,  locationHolder[user_id][1])
	        	GoogPlac(chat_id,locationHolder[user_id][0],locationHolder[user_id][1],'')
	        msg = MESSAGES['nearest']
	        #bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 
	        
def nearestSpc(bot, update):
	user_id = update.message.from_user.id
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/nearestSpc - "+name)
	
	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
	        msg = random.choice(MESSAGES['pmme']) % (name)
	        bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
	        msg = MESSAGES['nearest']
	        timestamp = datetime.datetime.utcnow()
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'nearestSpc', 'timestamp': timestamp }
	        log(info)
	        user = update.message.from_user
	        user_location = update.message.location
	        user = update.message.from_user
	        #print ("#################################### is"+ str(locationHolder[user_id][0]))
	        try:
	        	locationHolder[user_id] == KeyError
	        except KeyError:
	        	user_location = location_checker(bot, update)
	        else:
	        	print (locationHolder[user_id][0] ,  locationHolder[user_id][1])
	        	GoogPlac(chat_id,locationHolder[user_id][0],locationHolder[user_id][1],'SPC')
	        	
	        msg = MESSAGES['nearest']
	        #bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

def nearestShell(bot, update):
	user_id = update.message.from_user.id
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/nearestShell - "+name)
	
	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
	        msg = random.choice(MESSAGES['pmme']) % (name)
	        bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
	        msg = MESSAGES['nearest']
	        timestamp = datetime.datetime.utcnow()
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'nearestShell', 'timestamp': timestamp }
	        log(info)
	        user = update.message.from_user
	        user_location = update.message.location
	        user = update.message.from_user
	        #print ("#################################### is"+ str(locationHolder[user_id][0]))
	        try:
	        	locationHolder[user_id] == KeyError
	        except KeyError:
	        	user_location = location_checker(bot, update)
	        else:
	        	print (locationHolder[user_id][0] ,  locationHolder[user_id][1])
	        	GoogPlac(chat_id,locationHolder[user_id][0],locationHolder[user_id][1],'SHELL')
	        	
	        msg = MESSAGES['nearest']
	        #bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

def nearestCal(bot, update):
	user_id = update.message.from_user.id
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/nearestCal - "+name)
	
	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
	        msg = random.choice(MESSAGES['pmme']) % (name)
	        bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
	        msg = MESSAGES['nearest']
	        timestamp = datetime.datetime.utcnow()
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'nearestCal', 'timestamp': timestamp }
	        log(info)
	        user = update.message.from_user
	        user_location = update.message.location
	        user = update.message.from_user
	        #print ("#################################### is"+ str(locationHolder[user_id][0]))
	        try:
	        	locationHolder[user_id] == KeyError
	        except KeyError:
	        	user_location = location_checker(bot, update)
	        else:
	        	print (locationHolder[user_id][0] ,  locationHolder[user_id][1])
	        	GoogPlac(chat_id,locationHolder[user_id][0],locationHolder[user_id][1],'Caltex')
	        	
	        msg = MESSAGES['nearest']
	        #bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 

def nearestEsso(bot, update):
	user_id = update.message.from_user.id
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/nearestEsso - "+name)
	
	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
	        msg = random.choice(MESSAGES['pmme']) % (name)
	        bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
	        msg = MESSAGES['nearest']
	        timestamp = datetime.datetime.utcnow()
	        info = { 'user_name': name ,'user_id': user_id, 'request': 'nearestEsso', 'timestamp': timestamp }
	        log(info)
	        user = update.message.from_user
	        user_location = update.message.location
	        user = update.message.from_user
	        #print ("#################################### is"+ str(locationHolder[user_id][0]))
	        try:
	        	locationHolder[user_id] == KeyError
	        except KeyError: 
	        	user_location = location_checker(bot, update)
	        else:
	        	print (locationHolder[user_id][0] ,  locationHolder[user_id][1])
	        	GoogPlac(chat_id,locationHolder[user_id][0],locationHolder[user_id][1],'ESSO')
	        	
	        msg = MESSAGES['nearest']
	        #bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


#Grabbing and parsing the JSON data
def GoogPlac(chat_id,lat,lng,name):
  #making the url 
  AUTH_KEY = GOOGLE_PLACE_API_KEY
  LOCATION = str(lat) + "," + str(lng)
  RANKBY = 'distance'
  TYPES = 'gas_station'
  #if name == '': 
  	#name = 'false'
  MyUrl = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
           '?location=%s'
           '&rankby=%s'
           '&types=%s'
           '&keyword=%s'
           '&sensor=false&key=%s') % (LOCATION, RANKBY, TYPES, name , AUTH_KEY)
  #grabbing the JSON result
  response = urllib.request.urlopen(MyUrl)
  jsonRaw = response.read()
  jsonData = json.loads(jsonRaw.decode('utf-8'))

  IterJson(chat_id,jsonData["results"])

def IterJson(chat_id,Data):
  count = 0
  for place in Data:
  #for place in range(6):
  	if count < 5:
  		x = [place['name'], place['reference'], place['geometry']['location']['lat'],place['geometry']['location']['lng'], place['vicinity'],place['types']]
  		print (x)
  		msg = x
  		#if msg[0]
  		bot.sendVenue(chat_id,msg[2],msg[3],msg[0],msg[4])
  		count = count +1
  
def goodbye(bot, update):
	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/goodbye - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['goodbye']
		timestamp = datetime.datetime.utcnow()
		info = { 'user_name': name ,'user_id': user_id, 'request': 'goodbye', 'timestamp': timestamp }
		log(info)
		bot.sendMessage(chat_id=chat_id,text=msg,parse_mode="Markdown",disable_web_page_preview=1) 


# Unknown message reply
def unknown(bot, update):

	user_id = update.message.from_user.id 
	chat_id = update.message.chat.id
	message_id = update.message.message_id
	name = get_name(update.message.from_user)
	logger.info("/unknown - "+name)

	if (update.message.chat.type == 'group') or (update.message.chat.type == 'supergroup'):
		msg = random.choice(MESSAGES['pmme']) % (name)
		bot.sendMessage(chat_id=chat_id,text=msg,reply_to_message_id=message_id, parse_mode="Markdown",disable_web_page_preview=1) 
	else:
		msg = MESSAGES['unknown']
		timestamp = datetime.datetime.utcnow()
		info = { 'user_name': name ,'user_id': user_id, 'request': 'unknown', 'timestamp': timestamp }
		log(info)
		bot.sendMessage(chat_id=chat_id, text=(msg % name),parse_mode="Markdown",disable_web_page_preview=1)            

####################################################
# ADMIN FUNCTIONS
@restricted
def shutdown(bot,update):
    call("sudo shutdown -h now", shell=True)
    
@restricted
def getlog(bot,update):
    #ipdate Pi's IP address to the log
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    #Database update
    db = open("/home/pi/fuelwatchbotsg-master/localDataBase.txt","a+")
    db.write("Admin Request: Telebot is up with a IP Address of:" + ip_address)
    db.close()
    chat_id = update.message.chat.id
    bot.sendDocument(chat_id=chat_id, document=open('/home/pi/fuelwatchbotsg-master/localDataBase.txt', 'rb'))	

	
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
dp.add_handler(CommandHandler('updateLocation', location_checker))
dp.add_handler(CommandHandler('price', price))
dp.add_handler(CommandHandler('comment', comment))
dp.add_handler(CommandHandler('nearest', nearest))
dp.add_handler(CommandHandler('nearestspc', nearestSpc))
dp.add_handler(CommandHandler('nearestshell', nearestShell))
dp.add_handler(CommandHandler('nearestcal', nearestCal))
dp.add_handler(CommandHandler('nearestesso', nearestEsso))
dp.add_handler(CommandHandler('goodbye', goodbye))

#Admin Commands
dp.add_handler(CommandHandler('getlog', getlog))
dp.add_handler(CommandHandler('shutdown', shutdown))

'''
dp.add_handler(CommandHandler('commandstats',commandstats))
dp.add_handler(CommandHandler('locationstats',locationstats))
dp.add_handler(CommandHandler('joinstats',joinstats))
dp.add_handler(CommandHandler('liststations', liststations))
dp.add_handler(CommandHandler('listadmin', listadmin))
dp.add_handler(CommandHandler('todaysusers', todaysusers))
dp.add_handler(CommandHandler('promotets', promotets))
'''
# Location message
dp.add_handler(MessageHandler(Filters.location, location_checker))

### Unknown Even Handler
# Photo message
dp.add_handler(MessageHandler(Filters.photo, unknown))
# Sticker message
dp.add_handler(MessageHandler(Filters.sticker, unknown))
# Normal Text chat
dp.add_handler(MessageHandler(Filters.text, unknown))
# Unknown Command 
dp.add_handler(MessageHandler([Filters.command], unknown))


# log all errors
dp.add_error_handler(error)



#################################
# Polling 
logger.info("Starting polling")
updater.start_polling()
