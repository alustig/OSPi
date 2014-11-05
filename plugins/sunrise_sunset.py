# !/usr/bin/env python
from random import randint
import thread
import json
import time
import ephem, sys
from pyzipcode import ZipCodeDatabase
from itertools import ifilterfalse
import datetime, math

import web
import gv  # Get access to ospi's settings
from urls import urls  # Get access to ospi's URLs
from ospi import template_render
from webpages import ProtectedPage
from threading import Thread

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

sun_data = []

class SunriseSunset(Thread):
    def __init__(self):
        global sun_data
        Thread.__init__(self)
        self.daemon = True
        self.start()
        self.status = ''

        self._sleep_time = 0

        try:
            with open('./data/sunrise.json', 'r') as f:  # Read the location and station from file
                sun_data = json.load(f)
        except IOError:  # If file does not exist create the defaults
            sun_data = options_data()
            with open('./data/sunrise.json', 'w') as f:  # write default data to file
                json.dump(sun_data, f)
        print sun_data

    def add_status(self, msg):
        if self.status:
            self.status += '\n' + msg
        else:
            self.status = msg
        print msg

    def update(self):
        self._sleep_time = 0

    def _sleep(self, secs):
        self._sleep_time = secs
        while self._sleep_time > 0:
            time.sleep(1)
            self._sleep_time -= 1

    def run(self):
        global sun_data
        time.sleep(randint(3, 10))  # Sleep some time to prevent printing before startup information

        while True:
            if sun_data['auto_ss'] == 'on': # Plugin is enabled
                self.add_status("Calculating sun_data")
                sun_data = calculate()
                create_program()
                self._sleep(5)
        time.sleep(0.5)


sunny = SunriseSunset()


class sunrise_sunset(ProtectedPage):
    """Load an html page for entering zip code and choosing station"""
    global sun_data
    def GET(self):
        sun_data = calculate()
        return template_render.sunrise(sun_data)

class update(ProtectedPage):
    """Save user input to sunrise.json file"""
    def GET(self):
        qdict = web.input()
        if 'auto_ss' not in qdict:
            qdict['auto_ss'] = 'off'
        with open('./data/sunrise.json', 'w') as f:  # write the settings to file
            sun_data = calculate(qdict)
            json.dump(sun_data, f)
        
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
        'srs': 0,
        'sre': 0,
        'sss': 0,
        'sse': 0,
        'station': -1
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

def create_program():
    # Add/modify a program based on the user input
    global sun_data
    data = sun_data
    gv.pd[:] = list(ifilterfalse(determine, gv.pd)) # Remove prevously generated programs

    if data['auto_ss'] == 'on': # Plugin is enabled
        sr = data['sr'].split(":")
        sr = map(int, sr)
        srtime = datetime.datetime(100,1,1,sr[0],sr[1])
        srstd = datetime.timedelta(0,0,0,0,int(data['srs']))
        sretd = datetime.timedelta(0,0,0,0,int(data['sre']))
        srs = srtime-srstd
        sre = srtime+sretd
        srdur = (sre-srs).total_seconds()
        print "Sunrise:",srtime.time()
        print "On:",srs.time()
        print "Off:",sre.time()
        srs = str(srs.time()).split(":")
        start = int(srs[0])*60+int(srs[1])
        sre = str(sre.time()).split(":")
        end = int(sre[0])*60+int(sre[1])

        station = int(math.pow(2,int(data['station'])))
        newrise = [2,127,0,start,end,int(srdur),int(srdur),station] # 1st bit = 2 for sunrise
        gv.pd.append(newrise)

        ss = data['ss'].split(":")
        ss = map(int, ss)
        sstime = datetime.datetime(100,1,1,int(ss[0]),int(ss[1]))
        sse = data['sse'].split(":")
        sse = map(int, sse)
        if ss[1] > sse[1]:
            sse[1] = 60-ss[1]
            sse[0] -= 1
            ssm = sse[1]
        else:
            ssm = sse[1]-ss[1]
        sshr = sse[0]-ss[0]
        ssstd = datetime.timedelta(0,0,0,0,int(data['sss']))
        ssetd = datetime.timedelta(0,0,0,0,sshr*60+ssm)
        sss = sstime-ssstd
        sse = sstime+ssetd
        ssdur = (sse-sss).total_seconds()
        print "Sunset:",sstime.time()
        print "On:",sss.time()
        print "Off:",sse.time()
        sss = str(sss.time()).split(":")
        start = int(sss[0])*60+int(sss[1])
        sse = str(sse.time()).split(":")
        end = int(sse[0])*60+int(sse[1])

        newset = [2,127,0,start,end,int(ssdur),int(ssdur),station] # 1st bit = 2 for sunset
        gv.pd.append(newset)

    return True


def calculate():
    global sun_data
    data = sun_data
    zcdb = ZipCodeDatabase()
    local_zip = data['zip']
    zipcode = 0

    try:
        zipcode = zcdb[local_zip]
    except IndexError:
        print "not a valid zip, using a default: 10001"
        zipcode = zcdb[10001] # New York    

    now = datetime.datetime.now()
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
    data['sr'] = sunrise[0]+":"+sunrise[1]
    if (int(sunrise[0])<13):
        sunrise[0] = str(int(sunrise[0]))
        sunrise[2] = 'AM' 
    else:
        sunrise[0] = str(int(sunrise[0])-12)
        sunrise[2] = 'PM'

    sunset = str(ephem.localtime(o.next_setting(s)))
    sunset = sunset.split(' ')
    sunset = sunset[1].split(":")
    data['ss'] = sunset[0]+":"+sunset[1]
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
    data['sunrise'] = srise
    data['sunset'] = sset

    return data

def determine(a):
    c=0
    for i in a:
        if i == 2 and c == 0:
            return True
        c+=1
    return False