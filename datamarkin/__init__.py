from datamarkin import messenger, config

__version__ = "1.0.0.dev1"
__author__ = 'Datamarkin'

api_url = config.api_url
api_key = config.api_key

def status():
    api_route = '/users/me'
    url = api_url + api_route + '?access_token=' + api_key
    print(url)
    data = messenger.get_item(url)
    return data


class Status:
    def __init__(self, user_id, plan_id):
        self.id = user_id
        self.plan_id = plan_id
