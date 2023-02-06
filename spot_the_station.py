from bs4 import BeautifulSoup
import datetime as dt
import requests
import string_processing as sp



def parse_one_sighting(s):
    # Figure out current UTC offset from localtime
    utc_diff = dt.datetime.utcnow() - dt.datetime.now()
    # Data is comma-delimited within the raw text
    fields = s.split(',')
    # Only proceed if we have the right number of fields
    if len(fields) == 7:
        # Remove seconds part of formated datetime
        date_string = fields[0].replace(':00.0', '')
        # Convert to datetime object, local time
        date_time = dt.datetime.strptime(date_string, '%Y-%m-%d %H:%M') - utc_diff
        s = {'date_time':date_time,
             'date_text':sp.clean_chars(fields[1]),
             'time_text':sp.clean_chars(fields[2]),
             'visible':sp.clean_chars(fields[3]),
             'max_height':sp.clean_chars(fields[4]),
             'appears':sp.clean_chars(fields[5].replace('°', ' deg')),
             'disappears':sp.clean_chars(fields[6].replace('°', ' deg'))
            }
        return s
    return None

    
    
def parse_sightings(soup):
    # Returns empty list on any errors reading/parsing sightings
    sightings = []

    div = soup.find_all('div', {"id": "widget_info"})
    
    # If there's more than one div, something's wrong
    if len(div) > 1:
        return sightings
        
    # Pull out text
    div_contents = div[0].contents[0]
    # Fix spacing
    div_contents = div_contents.replace('  ', ' ')

    # Process each "sighting" chunk of the div text
    sightings_raw = div_contents.split('|')
    for raw_text in sightings_raw:
        s = parse_one_sighting(raw_text)
        if s is not None:
            sightings.append(s)
            
    return sightings
    


    
def get_sightings(country, region, city, location=None):
    
    if location is None:
        location = f'{city}, {region}, {country}'.replace('_', ' ')
    
    iss = {'fetched_on':dt.datetime.now(),
           'location':location,
           'country':country,
           'region':region,
           'city':city,
           'sightings':[],
           }
           
    url = f'https://spotthestation.nasa.gov/sightings/view.cfm?country={country}&region={region}&city={city}'
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        iss['sightings'] = parse_sightings(soup)
        
    return iss
    
