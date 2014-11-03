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


# Add a new url to open the data entry page.
urls.extend(['/ss', 'plugins.sunrise_sunset.sunrise_sunset', '/uss', 'plugins.sunrise_sunset.update_sunrise_sunset'])

# Add this plugin to the home page plugins menu
gv.plugin_menu.append(['Sunrise Sunset', '/ss'])


class sunrise_sunset(ProtectedPage):
    """Load an html page for entering zip code and choosing station"""

    def GET(self):
        try:
            with open('./data/sun.json', 'r') as f:  # Read the location and station from file
                sun_data = json.load(f)
        except IOError:  # If file does not exist
            sun_data = gv.sd['loc']
            with open('./data/sun.json', 'w') as f:  # write default data to file
                json.dump(sun_data, f)
        return template_render.sunrise(sun_data)

class update_sunrise_sunset(ProtectedPage):
        """Save user input to sun.json file"""
        