import datetime as dt
import requests
import string_processing as sp

def make_api_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.content.decode('utf-8')
        return data
    else:
        print("Unable to retrieve data.")
        return None

def get_bitcoin():
    base_url = 'https://blockchain.info/q/'
    bit = {
        'fetched_on': dt.datetime.now(),
        'usd_price': make_api_request(base_url + '24hrprice'),
        'blockheight': make_api_request(base_url + 'getblockcount'),
        'difficulty': make_api_request(base_url + 'getdifficulty'),
        'bcperblock': make_api_request(base_url + 'bcperblock'),
        'totalbc': make_api_request(base_url + 'totalbc'),
        'avgtxnumber': make_api_request(base_url + 'avgtxnumber')
    }

    return bit
