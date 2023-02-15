import datetime as dt
import requests
import string_processing as sp


    
def get_headline(s):
    pos = s.find('"headline":')
    if pos < 0:
        return None
    pos += 12
    s = s[pos:]
    pos = s.find('"description":')
    if pos < 0:
        return None
    pos -= 2
    s = s[0:pos]
    return sp.strip_tags(sp.clean_chars(s))


def get_summary(s):
    pos = s.find("\\u003c/p>")
    if pos < 0 or pos >= 500:
        return None
    pos -= 0
    s = s[9:pos]
    return sp.strip_tags(sp.clean_chars(s))
    
    
def get_news():
    
    news = {'fetched_on':dt.datetime.now(),
            'item_index':0,
            'items':[],
           }
    url = 'https://apnews.com'
    
    response = requests.get(url, headers={'Cache-Control': 'no-cache'})
    if response.status_code == 200:
        split_source = response.text.split('"firstWords":')
        for chunk in split_source:
            headline = get_headline(chunk)
            summary = get_summary(chunk)
            if headline is not None and summary is not None and headline.lower().find('top stories ') < 0:
                news['items'].append({'headline':headline, 'summary':summary})
    
    if len(news['items']) == 0:
        news['items'].append({'headline':'*** Newsfeed Unavailable ***', 'summary':'N/A'})
        
    return news