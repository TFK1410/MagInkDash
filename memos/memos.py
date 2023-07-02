###
# This is the module which we use to get the note from memos to add to the display
###

import logging
import requests

class Memos:
    def __init__(self):
        self.logger = logging.getLogger('maginkdash')

    def get_memo(self, domain, openId, tag):
        self.logger.info('Retrieving Memos memo from the domain {0} and tag {1}'.format(domain, tag))
        
        try:
            r = requests.get('https://' + domain + '/api/memo',
                             params={'openId': openId,
                                     'tag': tag},
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
        data = json_response['data']

        if len(data) == 0:
            return None
        else:
            return data[0]['content']
