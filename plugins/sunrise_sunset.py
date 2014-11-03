# !/usr/bin/env python
from random import randint
import thread
import json
import time

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
        except IOError:  # If file does not exist
            sun_data = gv.sd['loc']
            with open('./data/sunrise.json', 'w') as f:  # write default data to file
                json.dump(sun_data, f)
        return template_render.sunrise(sun_data)

class update(ProtectedPage):
    """Save user input to sun.json file"""
    def GET(self):
        qdict = web.input()
        if 'auto_ss' not in qdict:
            qdict['auto_ss'] = 'off'
        with open('./data/sunrise.json', 'w') as f:  # write the settings to file
            json.dump(qdict, f)
        checker.update()
        raise web.seeother('/ss')
