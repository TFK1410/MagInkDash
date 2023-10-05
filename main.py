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
import time
import schedule


if __name__ == '__main__':
    logger = logging.getLogger('maginkdash')

    # Basic configuration settings (user replaceable)
    configFile = open('config.json')
    config = json.load(configFile)

    calendars = config['calendars'] # Google Calendar IDs
    tasklists = config['tasklists'] # Google Task List IDs
    memos = dict()
    memos['domain'] = config['memos']['domain'] # Memos Domain
    memos['accessToken'] = config['memos']['accessToken'] # Memos accessToken
    memos['tag'] = config['memos']['tag'] # Memos tag
    displayTZ = timezone(config['displayTZ']) # list of timezones - print(pytz.all_timezones)
    numCalDaysToShow = config['numCalDaysToShow'] # Number of days to retrieve from gcal, keep to 3 unless other parts of the code are changed too
    imageWidth = config['imageWidth']  # Width of image to be generated for display.
    imageHeight = config['imageHeight']  # Height of image to be generated for display.
    rotateAngle = config['rotateAngle']  # If image is rendered in portrait orientation, angle to rotate to fit screen
    lat = config["lat"] # Latitude in decimal of the location to retrieve weather forecast for
    lon = config["lon"] # Longitude in decimal of the location to retrieve weather forecast for
    owm_api_key = config["owm_api_key"]  # OpenWeatherMap API key. Required to retrieve weather forecast.
    path_to_server_image = config["path_to_server_image"]  # Location to save the generated image

    # Create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('maginkdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
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
        
        # Retrieve Memo
        memoModule = Memos()
        currMemo = memoModule.get_memo(memos['domain'], memos['accessToken'], memos['tag'])

        # Render Dashboard Image
        renderService = RenderHelper(imageWidth, imageHeight, rotateAngle)
        renderService.process_inputs(currDate, current_weather, hourly_forecast, daily_forecast, eventList, taskList, numCalDaysToShow, currMemo, path_to_server_image)

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


