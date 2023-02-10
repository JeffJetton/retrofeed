from bs4 import BeautifulSoup
import datetime as dt
import requests
import string_processing as sp



# Populate an existing weather object with approprate values
# when weather data is not available
def assign_errors(wx):
    wx['conditions_location'] = 'N/A'
    wx['currently'] = 'N/A'
    wx['temp_f'] = 'N/A'
    wx['temp_c'] = ''
    wx['comfort'] = ''
    wx['last_update'] = 'N/A'
    wx['wind_speed'] = 'N/A'
    wx['visibility'] = 'N/A'
    wx['dewpoint'] = 'N/A'
    wx['periods'] = [{'timeframe':'Forecast Not Available',
                      'forecast':''}]
    return wx


def get_comfort_from_dewpoint(dp_text):
    dp = int(dp_text.split('F')[0])
    if dp < 50:
        return 'Dry'
    if dp <= 60:
        return 'Pleasant'
    if dp <= 65:
        return 'Slightly Humid'
    if dp <= 70:
        return 'Humid'
    if dp <= 75:
        return 'Very Humid'
    return 'Oppressive'
    

# Gets weather for a specific lat/lon in the US from weather.gov
# Returns a dictionary with various weather elements
def get_weather(lat, lon, location=None):
    
    wx = {'fetched_on':dt.datetime.now(),
          'location':location,
          'periods':[],
          'hazards':[] }
    #url = f'https://forecast.weather.gov/MapClick.php?textField1={lat}&textField2={lon}'
    url = f'https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}'
    #print(url)
    response = requests.get(url, headers={'Cache-Control':'no-cache', 'Pragma':'no-cache'})
    if response.status_code != 200:
        return(assign_errors(wx))     
    #print(response.headers)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Test check one element to make sure the site's showing weather
    if (soup.find('h2', 'panel-title')) is None:
        return(assign_errors(wx))

    wx['conditions_location'] = sp.clean_chars(soup.find('h2', 'panel-title').string)
    if wx['location'] == None:
        wx['location'] = ['conditions_location']
    wx['currently'] = sp.clean_chars(soup.find('p', 'myforecast-current').string)
    wx['temp_f'] = sp.clean_chars(soup.find('p', 'myforecast-current-lrg').string)
    wx['temp_c'] = sp.clean_chars(soup.find('p', 'myforecast-current-sm').string)
    
    # Various weather stats are stored as table data in the sole table
    cells = soup.find_all('td')
    key = None
    for cell in cells:
        if key is None:
            key = cell.string.lower().replace(' ', '_')
        else:
            wx[key] = sp.clean_chars(cell.string)
            key = None
    
    # Try to convert the "last_update" text to a real datetime value
    if 'last_update' in wx:
        # Assume year is current year (possibly inaccurate just after
        # midnight on New Year's Eve... oh well)
        dt_string = f"{dt.datetime.now().year} {wx['last_update']}"
        dt_object = dt.datetime.strptime(dt_string, '%Y %d %b %I:%M %p %Z')   #31 Jan 3:53 pm CST
        wx['last_update_dt'] = dt_object
    
    # Text description of the dewpoint
    wx['comfort'] = get_comfort_from_dewpoint(wx['dewpoint'])
    
    # Get period forecast from the alt-text of the weather icons
    icons = soup.find_all('img', 'forecast-icon')
    for icon in icons:
        alt_text = icon['alt']
        if alt_text is None or alt_text.strip() == '':
            continue
        split_text = alt_text.split(':', 1)
        if len(split_text) == 2:
            period = {'timeframe':sp.clean_chars(split_text[0]),
                      'forecast':sp.clean_chars(split_text[1])}
            wx['periods'].append(period)
    
    # Any hazard headlines?
    hazards = soup.find_all('a', 'anchor-hazards')
    for hazard in hazards:
        stripped_haz = hazard.contents[0].strip()
        if stripped_haz != 'Hazardous Weather Outlook' and stripped_haz != '':
            wx['hazards'].append(sp.clean_chars(stripped_haz))
        
    return wx
    
