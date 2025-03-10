"""
This project is designed for the Inkplate 10 display. However, since the server code is only generating an image, it can
be easily adapted to other display sizes and resolution by adjusting the config settings, HTML template and
CSS stylesheet. This code is heavily adapted from my other project (MagInkCal) so do take a look at it if you're keen.
As a dashboard, there are many other things that could be displayed, and it can be done as long as you are able to
retrieve the information. So feel free to change up the code and amend it to your needs.
"""

import datetime
import logging
import sys
import json
from datetime import datetime as dt
from pytz import timezone
from gcal.gcal import GcalModule
from owm.owm import OWMModule
from render.render import RenderHelper
from memos.memos import Memos
from dumbdo.dumbdo import Dumbdo
import time
import schedule

if __name__ == '__main__':
    logger = logging.getLogger('maginkdash')

    # Basic configuration settings (user replaceable)
    configFile = open('config.json')
    config = json.load(configFile)

    calendars = config['calendars'] # Google Calendar IDs
    tasklists = config['tasklists'] # Google Task List IDs
    
    memos_config = False
    if 'memos' in config:
        memos = dict()
        memos['domain'] = config['memos']['domain'] # Memos Domain
        memos['accessToken'] = config['memos']['accessToken'] # Memos accessToken
        memos['tag'] = config['memos']['tag'] # Memos tag
        memos_config = True
    elif 'dumbdo' in config:
        dumbdo = dict()
        dumbdo['domain'] = config['dumbdo']['domain'] # DumbDo Domain
        dumbdo['listName'] = config['dumbdo']['listName'] # DumbDo listName
    else:
        logger.error('Either memos or dumbdo has to be provided in the config. Memos will take precedence')
        exit(1)
    
    displayTZ = timezone(config['displayTZ']) # list of timezones - print(pytz.all_timezones)
    numCalDaysToShow = config['numCalDaysToShow'] # Number of days to retrieve from gcal, keep to 3 unless other parts of the code are changed too
    imageWidth = config['imageWidth']  # Width of image to be generated for display.
    imageHeight = config['imageHeight']  # Height of image to be generated for display.
    lat = config["lat"] # Latitude in decimal of the location to retrieve weather forecast for
    lon = config["lon"] # Longitude in decimal of the location to retrieve weather forecast for
    owm_api_key = config["owm_api_key"]  # OpenWeatherMap API key. Required to retrieve weather forecast.
    path_to_server_image = config["path_to_server_image"]  # Location to save the generated image
    nginx_server_dir = config['nginx']['server_dir']  # Path to the Nginx main folder for the html files to be transferred to
    nginx_serving_path = config['nginx']['serving_path']  # URL of the nginx for the browserless to use to render the html
    browserless_url = config['browserless']['url']  # Browserless url
    browserless_token = config['browserless']["token"]  # Browserless token

    # Create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('maginkdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    
    logger.info("Copying css and fonts to the nginx server directory")
    renderService = RenderHelper(imageWidth, imageHeight, nginx_server_dir=nginx_server_dir, nginx_serving_path=nginx_serving_path, 
                                 browserless_url=browserless_url, browserless_token=browserless_token)
    
    logger.info("Starting dashboard update")

    def job_run():
        # Retrieve Weather Data
        owmModule = OWMModule()
        current_weather, hourly_forecast, daily_forecast = owmModule.get_weather(lat, lon, owm_api_key)

        # Retrieve Calendar Data
        currDate = dt.now(displayTZ).date()
        calStartDatetime = displayTZ.localize(dt.combine(currDate, dt.min.time()))
        calEndDatetime = displayTZ.localize(dt.combine(currDate + datetime.timedelta(days=numCalDaysToShow-1), dt.max.time()))
        calModule = GcalModule()
        eventList = calModule.get_events(
            currDate, calendars, calStartDatetime, calEndDatetime, displayTZ, numCalDaysToShow)
        
        # Retrieve Timed Tasks
        taskList = calModule.get_tasks(
            currDate, tasklists, calStartDatetime, calEndDatetime, displayTZ, numCalDaysToShow)
        
        if memos_config:
            # Retrieve Memos
            memoModule = Memos()
            currNote = memoModule.get_memo(memos['domain'], memos['accessToken'], memos['tag'])
        else:
            # Retrieve DumbDo
            dd = Dumbdo()
            currNote = dd.get_list(dumbdo['domain'], dumbdo['listName'])

        # Render Dashboard Image
        renderService.process_inputs(currDate, current_weather, hourly_forecast, daily_forecast, eventList, taskList, numCalDaysToShow, currNote, path_to_server_image)

        logger.info("Completed dashboard update")
        
    job_run()
    
    schedule.every().hour.do(job_run)

    while 1:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        schedule.run_pending()


