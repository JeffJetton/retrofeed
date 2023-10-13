################################################################################
#
#  Spot the Station
#
#  Localized International Space Station sighting opportunities from
#  spotthestation.nasa.gov
#
#   - Initialization parameters:
#
#       refresh          Hours (not minutes!) to wait between webscrapes
#                        (default=24, minimum=1)
#       country          Country to pass to website (default = United_States)
#       region           Region to pass to website (default = Tennessee)
#       city             City to pass to website (default = Nashville)
#       location         Optional text to use as displayed location, overriding
#                        the display of country, region, and city
#
#       Visit spotthestation.nasa.gov and select city/town.  Examine resulting
#       URL to get the necessary country/region/city to use.
#
#
#   - Format parameters:
#
#       max_sightings    Maximum number of sighting opportunities to display,
#                        not including any that are in the past (which are
#                        automatically ignored).  Default = 3
#
#
#   Jeff Jetton, January-April 2023
#
################################################################################


import datetime as dt
from segment_parent import SegmentParent


DATE_FORMAT = "{ts '%Y-%m-%d %H:%M:%S'}"
INTRO = 'ISS Sightings provided by spotthestation.nasa.gov'


class Segment(SegmentParent):
                  
    def __init__(self, display, init):
        super().__init__(display, init, default_refresh=(24*60), default_intro=INTRO)
        # Set other init variables that are unique to this segment
        self.country = init.get('country', None)
        self.region = init.get('region', None)
        self.city = init.get('city', None)
        # Use defaults if any location info is still None
        if self.country is None or self.region is None or self.city is None:
            self.country = 'United_States'
            self.region = 'Tennessee'
            self.city = 'Nashville'
        self.location = init.get('location', f'{self.city}, {self.region}, {self.country}'.replace('_', ' '))


    def parse_one_sighting(self, raw_text):
        # Figure out current UTC offset from localtime
        utc_diff = dt.datetime.utcnow() - dt.datetime.now()
        # Data is comma-delimited within the raw text
        fields = raw_text.split(',')
        # Only proceed if we have the right number of fields
        if len(fields) == 7:
            # Remove seconds part of formated datetime
            date_string = fields[0].replace(':00.0', '')
            # Try to convert to datetime object, local time
            try:
                date_time = dt.datetime.strptime(date_string, DATE_FORMAT) - utc_diff
            except:
                return None
            s = {'date_time':date_time,
                 'date_text':self.d.clean_chars(fields[1]),
                 'time_text':self.d.clean_chars(fields[2]),
                 'visible':self.d.clean_chars(fields[3]),
                 'max_height':self.d.clean_chars(fields[4]),
                 'appears':self.d.clean_chars(fields[5].replace('°', ' deg')),
                 'disappears':self.d.clean_chars(fields[6].replace('°', ' deg'))
                }
            return s
        return None


    def parse_sightings(self, soup):
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
            s = self.parse_one_sighting(raw_text)
            if s is not None:
                sightings.append(s)
        return sightings


    def refresh_data(self):
        url = f'https://spotthestation.nasa.gov/sightings/view.cfm?country={self.country}&region={self.region}&city={self.city}'
        soup = self.get_soup(url)
        if soup is not None:
            self.data = {'fetched_on': dt.datetime.now()}
            self.data['sightings'] = self.parse_sightings(soup)


    def show(self, fmt):
        max_sightings = fmt.get('max_sightings', 3)
        if max_sightings < 0:
            max_sightings = 0
        if self.data_is_stale():
            self.d.print_update_msg('Updating Station Data')
            self.refresh_data()

        self.d.print_header('Spot the Station', '>', '<')
        self.d.newline()
    
        # Exit early if nothing to show at all
        if len(self.data['sightings']) == 0:
            self.d.print('No ISS Sightings Available')
            return

        self.d.print(self.location)
        self.d.print('Upcoming ISS Sightings:')
        
        num_shown = 0
        cutoff_dt = dt.datetime.now() - dt.timedelta(minutes=5)
        for s in self.data['sightings']:
            if s['date_time'] >= cutoff_dt and num_shown < max_sightings:
                self.d.newline(self.d.beat_delay)
                self.d.print(f"    {s['date_text']} @ {s['time_text']}")
                self.d.print(f"      Visible for {s['visible']}")
                self.d.print(f"      Max height {s['max_height']} Degrees")
                self.d.print(f"      From {s['appears']}")
                self.d.print(f"      To   {s['disappears']}")
                num_shown += 1

        # In case there were sightings, but they were all in the past...
        if num_shown == 0:
            self.d.print('No Future Sightings Available')



