# !/usr/bin/env python
from random import randint
import thread
import json
import time
import ephem, sys
from pyzipcode import ZipCodeDatabase
from datetime import datetime

import web
import gv  # Get access to ospi's settings
from urls import urls  # Get access to ospi's URLs
from ospi import template_render
from webpages import ProtectedPage

# gv.pd Reference
###########################
# 0: On or Off
# 1: Weekly (127) or interval
# 2: Something to do with interval (0 if weekly)
# 3: Start time in minutes from 00:00 hours (300 == 5:00 AM)
# 4: End time in minutes from 00:00 hours (720 == 12:00 PM)
# 5: Reccuring length in mins
# 6: Duration in seconds
# 7: Bitwise value of the stations the program applies to

# Add a new url to open the data entry page.
urls.extend(['/ss', 'plugins.sunrise_sunset.sunrise_sunset', '/uss', 'plugins.sunrise_sunset.update'])

# Add this plugin to the home page plugins menu
gv.plugin_menu.append(['Sunrise Sunset', '/ss'])

class sunrise_sunset(ProtectedPage):
    """Load an html page for entering zip code and choosing station"""
    def GET(self):
        try:
            with open('./data/sunrise.json', 'r') as f:  # Read the location and station from file
                sun_data = json.load(f)
        except IOError:  # If file does not exist create the defaults
            sun_data = options_data()
            with open('./data/sunrise.json', 'w') as f:  # write default data to file
                json.dump(sun_data, f)

        sun_data = calculate(sun_data)
        create_program(sun_data)
        return template_render.sunrise(sun_data)

class update(ProtectedPage):
    """Save user input to sunrise.json file"""
    def GET(self):
        qdict = web.input()
        if 'auto_ss' not in qdict:
            qdict['auto_ss'] = 'off'
        with open('./data/sunrise.json', 'w') as f:  # write the settings to file
            json.dump(qdict, f)
        create_program(sun_data)
        raise web.seeother('/ss')


################################################################################
# Helper functions:                                                            #
################################################################################

def options_data():
    # Defaults:
    result = {
        'auto_ss': 'off',
        'zip': '',
        'srs': '',
        'sre': '',
        'sss': '',
        'sse': '',
    }
    try:
        with open('./data/sunrise.json', 'r') as f:  # Read the settings from file
            file_data = json.load(f)
        for key, value in file_data.iteritems():
            if key in result:
                result[key] = value
    except Exception:
        pass

    return result

def create_program(data):
    # Add/modify a program based on the user input
    for i, p in enumerate(gv.pd):  # get both index and prog item
        try:
            p[8] # Flag to demarcate the auto generated program
        except IndexError:
            del gv.pd[i] # Remove the previously generated program

    if data['auto_ss'] == 'on': # Plugin is enabled
        newrise = [1,127,0,0,0,0,10,1] # 8th bit = 1 for sunrise
        gv.pd.append(newrise)
        newset = [1,127,0,0,0,0,20,2] # 8th bit = 2 for sunset
        gv.pd.append(newset)

    return True


def calculate(data):
    zcdb = ZipCodeDatabase()
    local_zip = data['zip']
    if local_zip == '':
        local_zip = 10001 # New York
    zipcode = zcdb[local_zip]

    now = datetime.now()
    o = ephem.Observer()
    o.pressure = 0
    o.horizon = '-0:34'
    o.date = now
    o.lat=str(zipcode.latitude)
    o.long=str(zipcode.longitude)
    s=ephem.Sun()
    data['loc'] = zipcode.city+", "+zipcode.state

    sunrise = str(ephem.localtime(o.next_rising(s)))
    sunrise = sunrise.split(' ')
    sunrise = sunrise[1].split(":")
    if (int(sunrise[0])<13):
        sunrise[0] = str(int(sunrise[0]))
        sunrise[2] = 'AM' 
    else:
        sunrise[0] = str(int(sunrise[0])-12)
        sunrise[2] = 'PM'

    sunset = str(ephem.localtime(o.next_setting(s)))
    sunset = sunset.split(' ')
    sunset = sunset[1].split(":")
    if (int(sunset[0])<13):
        sunset[0] = str(int(sunrise[0]))
        sunset[2] = 'AM' 
    else:
        sunset[0] = str(int(sunset[0])-12)
        sunset[2] = 'PM'

    srise = sunrise[0]+":"+sunrise[1]+" "+sunrise[2]
    sset = sunset[0]+":"+sunset[1]+" "+sunset[2]
    print "Rising ",srise
    print "Setting ",sset
    data ['sunrise'] = srise
    data ['sunset'] = sset

    return data