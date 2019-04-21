import requests
import json
import os


class Teams(object):
    def __init__(self):
        self.url = os.environ.get('TEAMS_URL', None)

    def send_message(self, title, text):
        payload_dic = {
            "title": title,
            "text": text,
        }
        response = requests.post(self.url, data=json.dumps(payload_dic))
        return response
