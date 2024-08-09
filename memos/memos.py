###
# This is the module which we use to get the note from memos to add to the display
# https://github.com/orgs/usememos/discussions/1024
###

import logging
import requests

class Memos:
    def __init__(self):
        self.logger = logging.getLogger('maginkdash')

    def get_memo(self, domain, accessToken, tag):
        self.logger.info('Retrieving Memos memo from the domain {0} and tag {1}'.format(domain, tag))
        
        try:
            r = requests.get(domain + '/api/v1/memos',
                             params={'filter': "tag_search == [\"" + tag + "\"]"},
                             headers={'Accept': 'application/json',
                                      'Authorization': 'Bearer ' + accessToken},
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

        text = data['memos'][0]['content']
        text = text.replace("#" + tag, "")
        text = text.strip()

        return text
