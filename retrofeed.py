# Standard library imports
import datetime as dt
import os
import random
import sys
import textwrap as tw
import time

# Retrofeed imports
import ap_news
import bitcoin 
import finance
import spot_the_station
import string_processing as sp
import weather



# Globals... Sooo many globals :-O
# (Might be nice to read these from a config file or something?)

VERSION = '0.1.3'

# Use faster timings if there are any command-line args at all
if len(sys.argv) == 1:
    SEGMENT_DELAY = 6          # Time between major segments
    SUBSEGMENT_DELAY = 1       # If a segment has multiple identical items, time between those
    PRINT_DELAY = 0.05         # Time between normally-printed characters
    NEWLINE_DELAY = 0.01       # Time between characters when doing a slow newline
    QUIZ_TIMER_DELAY = 0.2     # Time between LINE_WIDTH asterisks during quiz
else:
    print('(fast mode)')
    SEGMENT_DELAY = 1
    SUBSEGMENT_DELAY = 0.25
    PRINT_DELAY = 0.001
    NEWLINE_DELAY = 0.001
    QUIZ_TIMER_DELAY = 0.03

LINE_WIDTH = 40
VERBOSE_UPDATES = True     # Display a message when refreshing segment data?

# Weather settings.  Current conditions update every hour, but hazards/forecasts may
# change more frequently, so we use two different refresh intervals.
WX_MAX_PERIODS = 5         # Max forecast periods to show during full weather display
WX_LAT = 36.118542
WX_LON = -86.798358
WX_LOCATION = 'Nashville Intl Airport (BNA)'  # Overrides location from web page
WX_REFRESH_FETCH = dt.timedelta(minutes=22)   # Refresh interval based on 'fetched_on'
WX_REFRESH_UPDATE = dt.timedelta(minutes=65)  # Refresh interval based on 'last_update_dt'

# News settings
NEWS_ITEMS_AT_A_TIME = 3    # Number of news items to show during one NEWS_FULL segment
NEWS_MAX_ITEMS = 15         # Point after which news items start back at top
NEWS_MAX_HEADLINES = 15     # How many to show when just showing headlines
NEWS_REFRESH = dt.timedelta(minutes=19)

# ISS (Spot-the-Station) settings
ISS_COUNTRY = 'United_States'
ISS_REGION = 'Tennessee'
ISS_CITY = 'Nashville'
ISS_MAX_SIGHTINGS = 3
ISS_REFRESH = dt.timedelta(hours=12)

# Finance setting
FIN_REFRESH = dt.timedelta(minutes=13)
# TODO: Have one refresh time for trading hours, another for after

# Bitcoin setting
BITCOIN_REFRESH = dt.timedelta(minutes=10)  # Avg 10 minutes per bitcoin block

# Order of segments in the overall loop
# See loop in main() at end of file for possible options
SEGMENTS = ['DATE_TIME+',
            'WX_FULL',
            'DATE_TIME',
            'NEWS_FULL',
            'DATE_TIME',
            'WX_ONE_FCAST',
            'DATE_TIME',
            'NEWS_FULL',

            'ISS',

            'DATE_TIME+',
            'WX_FULL',
            'DATE_TIME',
            'NEWS_FULL',
            'DATE_TIME',
            'WX_ONE_FCAST',
            'DATE_TIME',
            'NEWS_FULL',

            'FINANCE',
            'BITCOIN',
           ]


###############################################################################
    
    
# Slow Print -- Similar to print() but with fun options
#               Wraps words at wrap_width characters if it is non-zero
def slowp(s='', end='\n', ucase=True, delay=PRINT_DELAY, wrap_width=0):
    if wrap_width > 0:
        lines = tw.wrap(s, wrap_width)
        # Call self for each line, but with wrapping off...
        for line in lines:
            slowp(line, end=end, ucase=ucase, delay=delay, wrap_width=0)
        return
    for c in s:
        if ucase:
            c = c.upper()
        print(c, end='', flush=True)
        time.sleep(delay) 
    print(end, end='', flush=True)
    time.sleep(delay)



# Slow Newline - Prints n spaces with a delay, then returns
#                Picks a random position to pause to stave off
#                screen burn-in (default = 0 = no pause)
def slown(pause_time=0, n=LINE_WIDTH, delay=NEWLINE_DELAY, final_delay=PRINT_DELAY):
    pause_pos = random.randrange(n)
    for i in range(n):
        print(' ', end='', flush=True)
        time.sleep(delay)
        if i == pause_pos:
            time.sleep(pause_time)
    print(flush=True)
    time.sleep(final_delay)



# Display the passed string as a segment header, surrounded by markers
def print_header(s, left_marker=' ', right_marker=None):
    if right_marker is None:
        right_marker = left_marker
    s = s.strip().upper()
    num_markers = 0
    if len(s) + 4 < LINE_WIDTH:
        num_markers = int((LINE_WIDTH - 4 - len(s)) / 2)
    slowp(left_marker * num_markers, end='')
    slowp('  ' + s + '  ', end='')
    slowp(right_marker * num_markers, end='')
    slowp()


# Display passed string as an "updating..." message
def print_update_msg(m):
    if VERBOSE_UPDATES:
        slowp(f'[{m}', end='')
        for i in range(3):
            time.sleep(SUBSEGMENT_DELAY)
            slowp('.', end='')
        time.sleep(SUBSEGMENT_DELAY)
        slowp(']')
        slown()
        #slown(SEGMENT_DELAY)



def show_date_time(descriptive=False):
    now = dt.datetime.now()
    date_text = now.strftime("%A, %B ")
    day_num = now.day
    date_text += str(day_num)
    if day_num in (1, 21, 31):
        date_text += 'st'
    elif day_num in (2, 22):
        date_text += 'nd'
    elif day_num in (3, 23):
        date_text += 'rd'
    else:
        date_text += 'th'
    time_text = sp.format_time(now)
    if descriptive:
        slowp('It is ' + date_text)
        slowp('Current time is ' + time_text)
    else:
        slowp(time_text + ' ' + date_text)



def show_finance(fin):
    
    # Check financials?
    now = dt.datetime.now()
    if fin is None or now - fin['fetched_on'] >= FIN_REFRESH:
        print_update_msg('Updating Financial Data')
        fin = finance.get_finance()
    
    print_header('Stocks', '$')
    slown()
        
    if 'CLOSED' in fin['market_message'].upper():
        slowp(fin['market_message'], wrap_width=LINE_WIDTH)
    else:
        slowp(f"As of {sp.format_time(fin['fetched_on'])}")
    
    for i in fin['indexes']:
        slown()
        slowp(f"    {i['name']:9}  {i['price']:>9}", wrap_width=LINE_WIDTH)
        slowp(f"               {i['delta']:>9}  {i['delta_pct']}", wrap_width=LINE_WIDTH)
        
    return fin




def show_weather(wx, forecast_periods=WX_MAX_PERIODS):
    
    # Get new weather object?
    now = dt.datetime.now()
    if (wx is None
        or now - wx['fetched_on'] >= WX_REFRESH_FETCH
        or ('last_update_dt' in wx and now - wx['last_update_dt'] >= WX_REFRESH_UPDATE)):
        print_update_msg('Checking for Weather Updates')
        wx = weather.get_weather(WX_LAT, WX_LON, WX_LOCATION)
        
    slowp(f'Weather at {wx["location"]}')
    slowp(f'As of {wx["last_update"]}')
    
    if len(wx['hazards']) > 0:
        for hazard in wx['hazards']:
            slown()
            slowp('!!! ' + hazard, wrap_width=LINE_WIDTH)
            
    slown()
    slowp(f'    Conditions   {wx["currently"]}')
    slowp(f'    Temperature  {wx["temp_f"]} ({wx["temp_c"]})')
    slowp(f'    Wind         {wx["wind_speed"]}')
    slowp(f'    Visibility   {wx["visibility"]}')
    slowp(f'    Dewpoint     {wx["dewpoint"]} {wx["comfort"]}')

    forecast_periods == min(forecast_periods, len(wx['periods']))
    if forecast_periods > 0:
        slown(SUBSEGMENT_DELAY)
        if forecast_periods > 1:
            slown()
            print_header('Extended Forecast...', '*')

        for period in wx['periods'][0:forecast_periods]:
            slown(SUBSEGMENT_DELAY)
            if forecast_periods > 1:
                slowp(period['timeframe'])
            slowp(period['forecast'], wrap_width=LINE_WIDTH)
            
    return wx



def show_news(news, items_at_a_time=NEWS_ITEMS_AT_A_TIME, max_items=NEWS_MAX_ITEMS, headlines=False):

    # Check for refresh
    if news is None or dt.datetime.now() - news['fetched_on'] >= NEWS_REFRESH:
        slown()
        print_update_msg('Getting Latest News')
        news = ap_news.get_news()
        
    if headlines:
        print_header('AP News Headlines', '!')
    else:
        print_header('AP News Summaries', '!')

    if headlines:
        # Headlines always start with first item. They don't cycle.
        start_index = 0
        end_index = min(items_at_a_time, max_items)
    else:
        # Restart item index?
        if news['item_index'] >= max_items or news['item_index'] >= len(news['items']):
            news['item_index'] = 0
        start_index = news['item_index']
        end_index = min(start_index + items_at_a_time, len(news['items']))

    for item in news['items'][start_index:end_index]:
        if not headlines:
            slown()
        slown(SUBSEGMENT_DELAY)
        slowp(item['headline'], wrap_width=LINE_WIDTH)
        if not headlines:
            slown()
            slowp(item['summary'], wrap_width=LINE_WIDTH)
            news['item_index'] += 1
            
    return news



def show_iss(iss, max_sightings=ISS_MAX_SIGHTINGS):
    
    # Generate or refresh object?
    if iss is None or dt.datetime.now() - iss['fetched_on'] >= ISS_REFRESH:
        print_update_msg('Updating Station Data')
        iss = spot_the_station.get_sightings(ISS_COUNTRY, ISS_REGION, ISS_CITY)
    
    print_header('Spot the Station', '>', '<')
    slown()
    
    # Exit early if nothing to show
    sightings = iss['sightings']
    if len(sightings) == 0:
        slowp('No ISS Sightings Available')
        return

    slowp(iss['location'])
    slowp('Upcoming ISS Sightings:')
    num_shown = 0
    cutoff_dt = dt.datetime.now()
    for s in sightings:
        if s['date_time'] >= cutoff_dt and num_shown < max_sightings:
            slown(SUBSEGMENT_DELAY)
            slowp(f"    {s['date_text']} @ {s['time_text']}")
            slowp(f"      Visible for {s['visible']}")
            slowp(f"      Max height {s['max_height']} Degrees")
            slowp(f"      From {s['appears']}")
            slowp(f"      To   {s['disappears']}")
            num_shown += 1

    return iss



def show_quiz():
    # TODO: State/country capitols, presidents, periodic table stuff, etc.?
    print_header('Quiz Goes Here', '?')
    slown()
    slowp("Wouldn't it be cool to implement some sort of quiz?", wrap_width=LINE_WIDTH)
    slown()
    for i in range(0, LINE_WIDTH):
        print('?', end='', flush=True)
        time.sleep(QUIZ_TIMER_DELAY)
    slowp()
    slown()
    slowp('Yes. Yes it would')


def show_bitcoin(bit):
    # Grab new bitcoin data if timer has elasped
    if bit is None or dt.datetime.now() - bit['fetched_on'] >= BITCOIN_REFRESH:
        print_update_msg('Getting Bitcoin Statistics')
        bit = bitcoin.get_bitcoin()

    # Format for readability
    difficulty = float(bit["difficulty"])    
    totalcirc = "{:,}".format(int(bit["totalbc"]) // 100_000_000)

    print_header('BITCOIN STATISTICS', '*')
    slown()
    slowp(f'As of {bit["fetched_on"].strftime("%b %d %Y %I:%M %p")}')
    slown()
    slowp(f'    USD Price       {bit["usd_price"]}')
    slown()
    slowp(f'    Blockheight     {bit["blockheight"]}')
    slowp(f'    Difficulty      {difficulty}')
    slowp(f'    Block Reward    {bit["bcperblock"]}')
    slowp(f'    Avg TXs/Block   {bit["avgtxnumber"]}')
    slowp(f'    Total Bitcoin   {totalcirc}')
    slown()
    return bit


def show_title():
    os.system('clear')
    for i in range(24):
        print()
    slowp(f'RETROFEED - VERSION {VERSION}')
    slowp('Copyright (C) Jeff Jetton')
    slown()
    slown()



def main():

    show_title()

    # Segment objects are generated by first call to their "show_" functions
    fin = None
    iss = None
    news = None
    wx = None
    bit = None

    # Main loop
    while True:
        for segment in SEGMENTS:
            slown()
            slown()
            
            # Show appropriate segment
            if segment == 'DATE_TIME':
                show_date_time()
            elif segment == 'DATE_TIME+':
                show_date_time(True)
            elif segment == 'FINANCE':
                fin = show_finance(fin)
            elif segment == 'WX_FULL':
                wx = show_weather(wx)
            elif segment == 'WX_NO_FCAST':
                wx = show_weather(wx, 0)
            elif segment == 'WX_ONE_FCAST':
                wx = show_weather(wx, 1)
            elif segment == 'NEWS_FULL':
                news = show_news(news)
            elif segment == 'NEWS_ONE_ITEM':
                news = show_news(news, 1)
            elif segment == 'NEWS_HLINES':
                news = show_news(news, NEWS_MAX_HEADLINES, headlines=True)
            elif segment == 'ISS':
                iss = show_iss(iss)
            elif segment == 'QUIZ':
                show_quiz()
            elif segment == 'BITCOIN':
                bit = show_bitcoin(bit)
            else:
                slown()
                print_header(f'Missing Segment "{segment}"', '*')
                
            slown()
            slown(SEGMENT_DELAY)
        


if __name__ == "__main__":
    main()
