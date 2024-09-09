"""
This script essentially generates a HTML file of the calendar I wish to display. It then fires up a headless Chrome
instance, sized to the resolution of the eInk display and takes a screenshot.

This might sound like a convoluted way to generate the calendar, but I'm doing so mainly because (i) it's easier to
format the calendar exactly the way I want it using HTML/CSS, and (ii) I can delink the generation of the
calendar and refreshing of the eInk display.
"""

from time import sleep
from datetime import timedelta
import pathlib
import string
import logging
import shutil
import requests
import json


class RenderHelper:

    def __init__(self, width, height, nginx_server_dir, nginx_servering_path, browserless_url, browserless_token):
        self.logger = logging.getLogger('maginkdash')
        self.currPath = str(pathlib.Path(__file__).parent.absolute())
        self.imageWidth = width
        self.imageHeight = height
        self.nginx_server_dir = nginx_server_dir
        self.nginx_servering_path = nginx_servering_path
        self.htmlFile = self.nginx_server_dir + 'dashboard.html'
        self.browserless_url = browserless_url
        self.browserless_token = browserless_token
        
        self._init_css_and_font()
    
    def _init_css_and_font(self):
        shutil.copytree(src=self.currPath + "/css", dst=self.nginx_server_dir, dirs_exist_ok=True)
        shutil.copytree(src=self.currPath + "/font", dst=self.nginx_server_dir, dirs_exist_ok=True)
        shutil.copy2(src=self.currPath + "/background.jpg", dst=self.nginx_server_dir)

    def get_screenshot(self, path_to_server_image):
        url = self.browserless_url + "/screenshot"
        params = {'token': self.browserless_token}
        headers = {'Cache-Control': 'no-cache', 'Content-type': 'application/json',
                   'Accept': 'image/png'}
        data = {
            'url': self.nginx_servering_path + "dashboard.html",
            'options': {
                'type': 'png'
            },
            'viewport': {
                'width': self.imageWidth,
                'height': self.imageHeight
            }
        }
        r = requests.post(url, data=json.dumps(data), headers=headers, params=params, stream=True)
        
        if r.status_code == 200:
            with open(self.currPath + '/dashboard.png', 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)

        self.logger.info('Screenshot captured and saved to file.')

    def get_short_time(self, datetimeObj, is24hour=False):
        datetime_str = ''
        if is24hour:
            datetime_str = '{}:{:02d}'.format(datetimeObj.hour, datetimeObj.minute)
        else:
            if datetimeObj.minute > 0:
                datetime_str = '.{:02d}'.format(datetimeObj.minute)

            if datetimeObj.hour == 0:
                datetime_str = '12{}am'.format(datetime_str)
            elif datetimeObj.hour == 12:
                datetime_str = '12{}pm'.format(datetime_str)
            elif datetimeObj.hour > 12:
                datetime_str = '{}{}pm'.format(str(datetimeObj.hour % 12), datetime_str)
            else:
                datetime_str = '{}{}am'.format(str(datetimeObj.hour), datetime_str)
        return datetime_str

    def process_inputs(self, current_date, current_weather, hourly_forecast, daily_forecast, event_list, task_list, num_cal_days, memos_text, path_to_server_image):

        # Read html template
        with open(self.currPath + '/dashboard_template.html', 'r') as file:
            dashboard_template = file.read()

        # Populate the date and events
        cal_events_list = []
        for i in range(num_cal_days):
            cal_events_text = ""
            
            if len(task_list[i]) > 0:
                cal_events_text += '<div class="event"><span class="event-time">Tasks: </span>'
                for task in task_list[i]:
                    cal_events_text += task['title'] + ', '
                cal_events_text = cal_events_text[:-2]
                cal_events_text += '</div>\n'
                    
            if len(event_list[i]) > 0:
                cal_events_text += ""
            else:
                cal_events_text += '<div class="event"><span class="event-time">None</span></div>'
            for event in event_list[i]:
                cal_events_text += '<div class="event">'
                if event["isMultiday"] or event["allday"]:
                    cal_events_text += event['summary']
                else:
                    cal_events_text += '<span class="event-time">' + self.get_short_time(event['startDatetime']) + '</span> ' + event['summary']
                cal_events_text += '</div>\n'
            cal_events_list.append(cal_events_text)

        # Append the bottom and write the file
        htmlFile = open(self.currPath + '/dashboard.html', "w")
        htmlFile.write(dashboard_template.format(
            day=current_date.strftime("%-d"),
            month=current_date.strftime("%B"),
            weekday=current_date.strftime("%A"),
            tomorrow=(current_date + timedelta(days=1)).strftime("%A"),
            dayafter=(current_date + timedelta(days=2)).strftime("%A"),
            # dayafter2=(current_date + timedelta(days=3)).strftime("%A"),
            # dayafter3=(current_date + timedelta(days=4)).strftime("%A"),
            events_today=cal_events_list[0],
            events_tomorrow=cal_events_list[1],
            events_dayafter=cal_events_list[2],
            # events_dayafter2=cal_events_list[3],
            # events_dayafter3=cal_events_list[4],
            # I'm choosing to show the forecast for the next hour instead of the current weather
            # current_weather_text=string.capwords(current_weather["weather"][0]["description"]),
            # current_weather_id=current_weather["weather"][0]["id"],
            # current_weather_temp=round(current_weather["temp"]),
            current_weather_text=string.capwords(hourly_forecast[1]["weather"][0]["description"]),
            current_weather_id=hourly_forecast[1]["weather"][0]["id"],
            current_weather_temp=round(hourly_forecast[1]["temp"]),
            today_weather_id=daily_forecast[0]["weather"][0]["id"],
            tomorrow_weather_id=daily_forecast[1]["weather"][0]["id"],
            dayafter_weather_id=daily_forecast[2]["weather"][0]["id"],
            today_weather_pop=str(round(daily_forecast[0]["pop"] * 100)),
            tomorrow_weather_pop=str(round(daily_forecast[1]["pop"] * 100)),
            dayafter_weather_pop=str(round(daily_forecast[2]["pop"] * 100)),
            today_weather_min=str(round(daily_forecast[0]["temp"]["min"])),
            tomorrow_weather_min=str(round(daily_forecast[1]["temp"]["min"])),
            dayafter_weather_min=str(round(daily_forecast[2]["temp"]["min"])),
            today_weather_max=str(round(daily_forecast[0]["temp"]["max"])),
            tomorrow_weather_max=str(round(daily_forecast[1]["temp"]["max"])),
            dayafter_weather_max=str(round(daily_forecast[2]["temp"]["max"])),
            memo_text=memos_text
        ))
        htmlFile.close()

        self.get_screenshot(path_to_server_image)
