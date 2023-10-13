################################################################################
#
#  United States Weather
#
#  Webscrapes weather info from weather.gov.
#
#   - Initialization parameters:
#
#       refresh    Minutes to wait between webscrapes (default=20).  Note that
#                  the weather will always be refreshed when the "last update"
#                  of the last fetch is a bit more than an hour old.  Use this
#                  refresh time to get more-frequent forecast updates if wanted.
#       lat, lon   Latitude amd longitude of weather/forecast location, used to 
#                  get data from weather.gov website.  (If either are missing,
#                  both default to lat 36.116453, lon -86.675228)
#       location   Description of location to display during weather segment
#                  If omitted, the "consitions" location from weather.gov for
#                  for the given lat & lon is used
#
#   - Format parameters:
#
#       forecast_periods  Maximum number of forecast periods, out of however
#                         are currently available, to show after giving weather
#                         Can be zero.  Default is 5, max is 15.
#                         If it's 2 or higher, forecasts are preceeded by an
#                         "extended forecast" header.
#
#
#   Jeff Jetton, Jan-Mar 2023
#
################################################################################


import datetime as dt
from segment_parent import SegmentParent

INTRO = 'Weather provided by weather.gov'


class Segment(SegmentParent):
    
    utc_offsets = {'EST':'-0500', 'CST':'-0600', 'MST':'-0700', 'PST':'-0800', 'AKST':'-0900', 'HST':'-1000',
                   'EDT':'-0400', 'CDT':'-0500', 'MDT':'-0600', 'PDT':'-0700', 'AKDT':'-0800', 'HDT':'-0900' }
                  
    def __init__(self, display, init):
        super().__init__(display, init, default_refresh=20, default_intro=INTRO)
        # Set other init variables unique to this segment
        self.location = init.get('location', None)
        self.lat = init.get('lat', None)
        self.lon = init.get('lon', None)
        # Use default lat/lon if either is missing
        if self.lat is None or self.lon is None:
            self.lat = 36.116453
            self.lon = -86.675228
            self.location = 'Default Location (BNA)'


    @classmethod
    def get_comfort_from_dewpoint(cls, dp_text):
        dp = int(dp_text.split('F')[0])
        if dp < 50:
            return 'Dry'
        if dp <= 60:
            return 'Pleasant'
        if dp <= 65:
            return 'A Bit Humid'
        if dp <= 70:
            return 'Humid'
        if dp <= 75:
            return 'Very Humid'
        return 'Oppressive'


    def assign_na(self):
        self.data['conditions_location'] = 'N/A'
        self.data['currently'] = 'N/A'
        self.data['temp_f'] = 'N/A'
        self.data['temp_c'] = 'N/A'
        self.data['humidity'] = 'N/A'
        self.data['barometer'] = 'N/A'
        self.data['comfort'] = ''
        self.data['last_update'] = 'N/A'
        self.data['wind_speed'] = 'N/A'
        self.data['visibility'] = 'N/A'
        self.data['dewpoint'] = 'N/A'
        self.data['periods'] = [{'timeframe':'Forecast Not Available',
                                 'forecast':''}]

    @classmethod
    def string_to_dt(cls, s):
        # Convert a string in weather.gov's "last update" format to a
        # timezone-aware datetime object, so we can compare to current
        # date/time and check if the weather info is a bit older than one hour
        dt_string = s.strip()
        # Ensure that day and hour are zero-padded, to satisfy some systems
        if dt_string[1] == ' ':
            dt_string = '0' + dt_string
        col_pos = dt_string.find(':')
        if dt_string[col_pos-2] == ' ':
            dt_string = dt_string[0:col_pos-1] + '0' + dt_string[col_pos-1:]
        # Assume year is current year (possibly inaccurate just after
        # midnight on New Year's Eve... oh well)
        dt_string = f"{dt.datetime.now().year} {dt_string}"
        # Pull out the last word (presumably the time zone code)
        tz = dt_string[dt_string.rfind(' ')+1:]
        # If it matches an offset, replace code with offset and convert
        if tz in cls.utc_offsets:
            dt_string = dt_string.replace(tz, cls.utc_offsets[tz])
            dt_object = dt.datetime.strptime(dt_string, '%Y %d %b %I:%M %p %z')
        else:
            # Otherwise, convert with local timezone info
            dt_string = dt_string.replace(tz, '').strip()
            dt_object = dt.datetime.strptime(dt_string, '%Y %d %b %I:%M %p').astimezone()
        return dt_object


    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     'periods':[],
                     'hazards':[]}

        url = f'https://forecast.weather.gov/MapClick.php?lat={self.lat}&lon={self.lon}'
        soup = self.get_soup(url)
        # Even if not None, also check one element to make sure the site is
        # currently showing weather (i.e. isn't down but still returning soup)
        if soup is None or soup.find('h2', 'panel-title') is None:
            self.assign_na()
            return

        # Parse away...
        self.data['conditions_location'] = self.d.clean_chars(soup.find('h2', 'panel-title').string)
        # If object wasn't instantiated with a location, set it to whatever came back from fetch
        if self.location == None or self.location.strip() == '':
            self.location = self.data['conditions_location']
        self.data['currently'] = self.d.clean_chars(soup.find('p', 'myforecast-current').string)
        self.data['temp_f'] = self.d.clean_chars(soup.find('p', 'myforecast-current-lrg').string)
        self.data['temp_c'] = self.d.clean_chars(soup.find('p', 'myforecast-current-sm').string)

        # Various weather stats are stored as table data in the sole table
        cells = soup.find_all('td')
        key = None
        for cell in cells:
            if key is None:
                key = cell.string.lower().replace(' ', '_')
            else:
                self.data[key] = self.d.clean_chars(cell.string)
                key = None

        # Try to convert the "last_update" text to a real datetime value
        if 'last_update' in self.data:
            self.data['last_update_dt'] = self.string_to_dt(self.data['last_update'])

        # Text description of the dewpoint
        self.data['comfort'] = self.get_comfort_from_dewpoint(self.data['dewpoint'])

        # Get period forecast from the alt-text of the weather icons
        icons = soup.find_all('img', 'forecast-icon')
        for icon in icons:
            alt_text = icon['alt']
            if alt_text is None or alt_text.strip() == '':
                continue
            split_text = alt_text.split(':', 1)
            if len(split_text) == 2:
                period = {'timeframe':self.d.clean_chars(split_text[0]),
                          'forecast':self.d.clean_chars(split_text[1])}
                self.data['periods'].append(period)

        # Any hazard headlines?
        hazards = soup.find_all('a', 'anchor-hazards')
        for hazard in hazards:
            stripped_haz = hazard.contents[0].strip()
            if stripped_haz != 'Hazardous Weather Outlook' and stripped_haz != '':
                self.data['hazards'].append(self.d.clean_chars(stripped_haz))


    # Override to add one more stale condition
    def data_is_stale(self):
        # Start witht the usual check:  Data is stale if we don't have any
        # weather yet (self.data still None) or refresh time has elapsed:
        if super().data_is_stale():
            return True
        else:
            # Data is always stale if (slightly) more than an hour has gone by
            now = dt.datetime.now()
            return 'last_update_dt' in self.data and now.astimezone() - self.data['last_update_dt'] >= dt.timedelta(minutes=62)



    def show(self, fmt):
        forecast_periods = fmt.get('forecast_periods', 5)
        forecast_periods = self.clamp(forecast_periods, 0, 15)

        if self.data_is_stale():
            self.d.print_update_msg('Checking for Weather Updates')
            self.refresh_data()

        self.d.print(f'Weather at {self.location}')
        self.d.print(f'As of {self.data["last_update"]}')
    
        if len(self.data['hazards']) > 0:
            for hazard in self.data['hazards']:
                self.d.newline()
                self.d.print('!!! ' + hazard)
            
        self.d.newline()
        self.d.print(f'    Conditions   {self.data["currently"]}')
        self.d.print(f'    Temperature  {self.data["temp_f"]} ({self.data["temp_c"]})')
        self.d.print(f'    Wind         {self.data["wind_speed"]}')
        self.d.print(f'    Visibility   {self.data["visibility"]}')
        self.d.print(f'    Dewpoint     {self.data["dewpoint"]} {self.data["comfort"]}')
        # TODO: only show comfort if warm enough?

        forecast_periods == min(forecast_periods, len(self.data['periods']))
        if forecast_periods > 0:
            self.d.newline(self.d.beat_delay)
            if forecast_periods > 1:
                self.d.newline()
                self.d.print_header('Extended Forecast', '*')

            for period in self.data['periods'][0:forecast_periods]:
                self.d.newline(self.d.beat_delay)
                if forecast_periods > 1:
                    self.d.print(period['timeframe'])
                self.d.print(period['forecast'])


