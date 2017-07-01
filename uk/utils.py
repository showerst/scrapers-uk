import json
import requests

def get_all_pages(url, url_args={}):
    return_val = []
    arguments = {'_pageSize':500,
                 '_page':1}
    arguments.update(url_args)
    page = requests.get(url, params=arguments)
    json_obj = json.loads(page.content)
    return_val = json_obj['result']['items']

    while 'next' in json_obj['result']:
        # the next url doesn't keep our page size, so tack it on
        url = "{}&_pageSize=500".format(json_obj['result']['next'])
        page = requests.get(url)
        json_obj = json.loads(page.content)
        return_val = return_val + json_obj['result']['items']

    return return_val
