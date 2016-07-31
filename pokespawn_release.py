#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 
    @author: github.com/dhernandez98 - twitter.com/MrKemula
    This simple Python script gathers the active Pokemon in the specified zone of PokeMiner and uses both Telegram and Twitter API to send alerts.
'''

# imports
import logging
import telegram
import db
import json
import time
#import tweepy # UNCOMMENT THIS LINE TO USE TWITTER
import sys
import random

from datetime import datetime
from geopy.geocoders import GoogleV3
from telegram.error import NetworkError
from time import sleep

# just get the Pokemon names
with open('locales/pokemon.en.json') as f:
    pokemon_names = json.load(f)
    
# set UTF8 for emojis support
reload(sys)  
sys.setdefaultencoding('utf8')

# init geolocator API. You can use any geolocation service here, but Google is suggested.
geolocator = GoogleV3(api_key = 'GMAPS API KEY')

# UNCOMMENT THIS BLOCK TO USE TWITTER
'''auth = tweepy.OAuthHandler('CONSUMER KEY', 'CONSUMER SECRET')  
auth.set_access_token('ACCESS TOKEN', 'ACCESS TOKEN SECRET') # to obtain these, check out the tools folder.

global api
api = tweepy.API(auth)  
'''
# we use emojis to show the rarity of a Pokemon.
sparkles = u'\U00002728'
whiteball = u'\U000026AA'
blackball = u'\U000026AB'
redball = u'\U0001F534'
blueball = u'\U0001F535'

# create a list where detected Pokemon will be stored
allPokList = []

def main():
    print 'PokeSpawn v1.01 - @MrKemula'
    
    # connect to Telegram's bot
    bot = telegram.Bot('TELEGRAM BOT SECRET')
    
    while True:
        try:
            PokListener(bot)
        except NetworkError:
            #puta vida. ya se ha caido el internet.
            print "Network error... Retrying in 2 seconds.."
            sleep(2)

def PokIDtoStars(argument):
    # wow, dirty code here! the format is -> PokemonID: rarity (from 1 to 5)
    switcher = {
        1: 2,
        2: 3,
        3: 4,
        4: 2,
        5: 3,
        6: 4,
        7: 2,
        8: 3,
        9: 4,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1,
        15: 1,
        16: 1,
        17: 1,
        18: 1,
        19: 1,
        20: 1,
        21: 1,
        22: 1,
        23: 1,
        24: 1,
        25: 1,
        26: 2,
        27: 1,
        28: 1,
        29: 1,
        30: 1,
        31: 1,
        32: 1,
        33: 1,
        34: 1,
        35: 1,
        36: 1,
        37: 1,
        38: 4,
        39: 1,
        40: 1,
        41: 1,
        42: 1,
        43: 1,
        44: 1,
        45: 1,
        46: 1,
        47: 1,
        48: 1,
        49: 1,
        50: 1,
        51: 1,
        52: 1,
        53: 1,
        54: 1,
        55: 2,
        56: 1,
        57: 1,
        58: 1,
        59: 1,
        60: 1,
        61: 1,
        62: 1,
        63: 1,
        64: 2,
        65: 3,
        66: 1,
        67: 1,
        68: 1,
        69: 1,
        70: 1,
        71: 1,
        72: 1,
        73: 2,
        74: 1,
        75: 1,
        76: 1,
        77: 1,
        78: 1,
        79: 1,
        80: 1,
        81: 1,
        82: 2,
        83: 2,
        84: 1,
        85: 1,
        86: 1,
        87: 1,
        88: 2,
        89: 3,
        90: 1,
        91: 2,
        92: 1,
        93: 2,
        94: 3,
        95: 1,
        96: 1,
        97: 2,
        98: 1,
        99: 1,
        100: 1,
        101: 2,
        102: 1,
        103: 1,
        104: 1,
        105: 1,
        106: 1,
        107: 1,
        108: 1,
        109: 1,
        110: 2,
        111: 1,
        112: 1,
        113: 1,
        114: 1,
        115: 3,
        116: 1,
        117: 2,
        118: 1,
        119: 1,
        120: 1,
        121: 3,
        122: 1,
        123: 3,
        124: 1,
        125: 2,
        126: 2,
        127: 1,
        128: 2,
        129: 1,
        130: 3,
        131: 4,
        132: 4,
        133: 1,
        134: 3,
        135: 3,
        136: 2,
        137: 3,
        138: 2,
        139: 3,
        140: 1,
        141: 2,
        142: 2,
        143: 4,
        144: 5,
        145: 5,
        146: 5,
        147: 1,
        148: 3,
        149: 4,
        150: 5,
        151: 5,
    }
    return switcher.get(argument, 1)
        
def EmojiFromRank(raid):
    if raid == 1:
        return sparkles + whiteball
    elif raid == 2:
        return sparkles + blackball
    elif raid == 3:
        return sparkles + blueball
    elif raid == 4:
        return sparkles + redball
    elif raid == 5:
        return sparkles + redball + sparkles + redball
    else:
        return sparkles

def PokListener(bot):
    session = db.Session()
    pokemons = db.get_sightings(session)
    session.close()
    
    pokeids = [2,3,5,6,8,9,26,31,34,38,55,64,65,68,73,82,83,88,89,91,92,93,94,97,110,115,117,121,122,123,124,125,128,130,131,132,134,135,136,137,139,142,143,144,145,147,146,148,149,150,151] # List of Pokemon we want to show. 
    commonPok = [64, 122, 147] # we'll store some rare Pokemons but common in our zone. This will trigger a RNG.

    now = time.time()
    for pokemon in pokemons:
        if abs(pokemon.expire_timestamp) > now:
            time_remaining = abs(pokemon.expire_timestamp) - now
            if time_remaining >= 200:
                if pokemon.spawn_id not in allPokList:
                    if pokemon.pokemon_id in pokeids:
                        # uncomment the block above to limit the alerts to some Pokemon (for example, there will be a pertentage to send alert if Flareon, Electrabuz...)
                        '''if pokemon.pokemon_id in commonPok:
                            gluck = random.randint(0, 1) # 50%...
                            if gluck == 0:
                                allPokList.append(pokemon.spawn_id)
                                continue'''
                        name = pokemon_names[str(pokemon.pokemon_id)]
                        datestr = datetime.fromtimestamp(pokemon.expire_timestamp)
                        dateoutput = datestr.strftime("%H:%M:%S")
                        
                        location = geolocator.reverse((pokemon.lat, pokemon.lon), True)
                        useloc = location.address.split(', 230') #this is used to trim the location. If string is >140 chars, Twitter API will crash. Change to the first digits of your ZIP code. If ZIP code is 23002, i'll put 230
                        print '[-] A ' + name + ' was found in ' + useloc[0] + '. ' + str(round(time_remaining)) + 's remaining.' 
                        allPokList.append(pokemon.spawn_id)
                        message = EmojiFromRank(PokIDtoStars(pokemon.pokemon_id)) + ' <b>' + name + '</b> was found in <a href="https://www.google.com/maps/dir/Current+Location/'+ pokemon.lat +',' + pokemon.lon +'">' + useloc[0] + '</a>. Disappear time: <b>' + dateoutput + '</b>'
                        
                        bot.sendMessage('@CHANNEL/GROUP', message, 'html') # the @name of your channel/group. The bot MUST be added as administrator if channel.
                        bot.sendLocation('@CHANNEL/GROUP', pokemon.lat, pokemon.lon) # same, the @name of your channel/group where the location will be send to.
                        
                        # UNCOMMENT THIS BLOCK TO USE TWITTER
                        '''twdatestr = datetime.fromtimestamp(now)
                        twdateoutput = datestr.strftime("%d/%m/%Y") # Spanish' default date format. Change to %m/%d/%Y if you're not Spanish.
                        message = '[' + twdateoutput + '] ' + EmojiFromRank(PokIDtoStars(pokemon.pokemon_id)) + name + ' appeared at ' + useloc[0] + '. Disappear time: ' + dateoutput + '. http://www.google.com/maps/dir/Current+Location/' + pokemon.lat + ',' + pokemon.lon
                        api.update_status(message, (pokemon.lat, pokemon.lon))'''

if __name__ == '__main__':
    main()