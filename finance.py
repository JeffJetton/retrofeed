from bs4 import BeautifulSoup
import datetime as dt
import requests
import string_processing as sp


SYMBOLS = {'^GSPC':'S&P 500',
           '^DJI': 'Dow Jones',
           '^IXIC':'NASDAQ',
           '^RUT' :'Russell',
          }
          
          
def parse_indexes(streamers):
    ind = []
    curr_symbol = ''
    i = {'symbol':''}

    for s in streamers:
        symbol = s['data-symbol']
        # Check for new symbol
        if symbol != curr_symbol:
            # Close out any current index
            if i['symbol'] != '':
                ind.append(i)
            # Set up new index
            i = {'symbol':symbol, 'price':'N/A', 'delta':'N/A', 'delta_pct':'N/A'}
            curr_symbol = symbol
        # Check for price
        if s['data-field'] == 'regularMarketPrice':
            i['price'] = s.contents[0]
        elif s['data-field'] == 'regularMarketChange':
            i['delta'] = s.contents[0].contents[0]
        elif s['data-field'] == 'regularMarketChangePercent':
            i['delta_pct'] = s.contents[0].contents[0]

    # Append last index
    ind.append(i)
    return ind


def process_indexes(ind):
    # Translates symbols and only returns the symbols we have names for
    new_ind = []
    for i in ind:
        if i['symbol'] not in SYMBOLS:
            continue
        i['name'] = SYMBOLS[i['symbol']]
        new_ind.append(i)
        
    return new_ind


    
def get_finance():
    
    fin = {'fetched_on':dt.datetime.now(),
           'market_message':'',
           'indexes':[],
           }
    url = 'https://finance.yahoo.com'
    
    response = requests.get(url, headers={'Cache-Control': 'no-cache'})
    if response.status_code != 200:
        return fin
        
    soup = BeautifulSoup(response.text, 'html.parser')   
    msg = soup.find('span', {'data-id':'mk-msg'})
    if len(msg) > 0:
        fin['market_message'] = sp.clean_chars(msg.contents[0])
    streamers = soup.find_all('fin-streamer')
    fin['indexes'] = parse_indexes(streamers)
    fin['indexes'] = process_indexes(fin['indexes'])
    return fin


