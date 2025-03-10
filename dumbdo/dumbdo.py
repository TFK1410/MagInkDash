###
# This is the module which we use to get the todo list from the DumbDo (https://github.com/DumbWareio/DumbDo) to add to the display
###

import logging
import requests

class Dumbdo:
    def __init__(self):
        self.logger = logging.getLogger('maginkdash')

    def get_list(self, domain, listName):
        self.logger.info('Retrieving ToDo list from the domain {0} and list {1}'.format(domain, listName))
        
        try:
            r = requests.get(domain + '/api/todos',
                             headers={'Accept': 'application/json'},
                             timeout=10)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            self.logger.info("Http Error:",errh)
            return None
        except requests.exceptions.ConnectionError as errc:
            self.logger.info("Error Connecting:",errc)
            return None
        except requests.exceptions.Timeout as errt:
            self.logger.info("Timeout Error:",errt)
            return None
        except requests.exceptions.RequestException as err:
            self.logger.info("OOps: Something Else",err)
            return None
            
        json_response = r.json()
        data = json_response

        if len(data) == 0:
            return None

        text = ''
        for entry in data[listName]:
            if entry['completed'] == False:
                text = text + '\n• ' + entry['text']
        text = text.strip()
        
        return text