# Standard library imports
import datetime as dt
import importlib.util
import os
import sys
import textwrap as tw
import time

# RetroFeed imports
from display import Display



# Globals...
VERSION = '0.2.0'
EXPECTED_TABLES = ['display', 'segments', 'playlist']

# The config dictionary sets all parameters, specifies segments to use, and display order
# Eventually this will be read in from a config.toml file, but I'm waiting until the
# standard Rasperry Pi OS install includes Python 3.11 (which has tomllib)
CONFIG = {'display': {'height': 24,
                      'width': 40,
                      'cps': 20,
                      'newline_cps': 100,
                      'beat_seconds': 1,
                      'force_uppercase': True,
                      'verbose_updates': True,
                      '24hr_time':True,
                      'show_intros':True,
                     },

          # Segment modules must be declared and given a name (key) before use.
          # Each must have at least a 'module' value specifying a .py file in
          # the 'segments' directory.  Other keys/values depend on the segment.
          'segments': {'otd': {'module': 'wiki_on_this_day.py'},
                       'lucky': {'module': 'lucky_numbers.py'},
                       'nash_wx': {'module': 'us_weather.py',
                                   'refresh': 15,
                                   'lat': 36.118542,
                                   'lon': -86.798358,
                                   'location': 'Nashville Intl Airport (BNA)'},
                       # Example of declaring a segment module twice, with a
                       # different name (key) and different initialization
                       # parameters.  Also note that the ".py" at the end of a
                       # segment module's name is optional and can be dropped.
                       'bos_wx': {'module': 'us_weather',
                                  'refresh': 30,
                                  'lat': 42.365738,
                                  'lon': -71.017027,
                                  'location': 'Boston Logan Intl Airport'},
                       'news': {'module': 'ap_news'},
                       'iss': {'module': 'spot_the_station', 'country':'United_States', 'region':'Tennessee', 'city':'Nashville'},
                       'fin': {'module': 'yahoo_finance'},
                       'datetime': {'module': 'date_time.py'}
                      },

          # Segment names in the 'order' part of the playlist must match the
          # names (keys) given above.  They can either be a string by itself,
          # or a two-element list with the name (string) as the first element
          # and a dictionary of format specifications as the second.
          'playlist': {'segment_pause': 6,
                       'order': ['datetime',
                                 'nash_wx',
                                 'datetime',
                                 'news',
                                 'otd',
                                 'datetime',
                                 'fin',
                                 # Ask datetime to use a slightly different
                                 # format for this showing...
                                 ['datetime', {'format': 'short'}],
                                 'iss',
                                 'datetime',
                                 # Use abbreviated forecase for Boston
                                 ['bos_wx', {'forecast_periods':1}],
                                 'datetime',
                                 'news',
                                 'datetime',
                                 'lucky',
                                 'otd',
                                ]
                      }
         }



def check_config_tables(config):
    # Just throw an error if any of the main three sections aren't in config
    # Nothing fancy...
    missing_tables = []
    for table in EXPECTED_TABLES:
        if table not in config:
            missing_tables.append(table)
    if len(missing_tables) > 0:
        raise RuntimeError('Table(s) missing in config: ' + ', '.join(missing_tables))
    # Make sure each declared segment has at least a module key
    bad_segments = []
    for key in config['segments']:
        if 'module' not in config['segments'][key]:
            bad_segments.append(key)
    if len(bad_segments) > 0:
        raise RuntimeError('No module defined for segment(s) in config: ' + ', '.join(bad_segments))
            


def override_timings(config):
    config['display']['cps'] = 1000
    config['display']['newline_cps'] = 1000
    config['display']['beat_seconds'] = 0.1
    config['playlist']['segment_pause'] = 1
    return config



def instantiate_segments(config, d):
    # Segments dictionary holds references to all instantiated objects
    segments = {}
    # This just keeps track of unique modules already instantiated,
    # so we only call show_intro() once per module
    instantiated = []
    # Go through config and initialize all required segments
    # We don't check to see if they exist, so... fingers crossed!
    for key in config['segments']:
        mod_name = config['segments'][key]['module']
        # Just in case the user put the .py on the end...
        if mod_name.endswith('.py'):
            mod_name = mod_name[0:-3]
        # Import, instantiate, and add to segments dictionary
        # using the specified key (which will match in playlist)
        module = importlib.import_module('segments.' + mod_name)
        segments[key] = module.Segment(d, config['segments'][key])
        # If we haven't already, give module chance to introduce itself
        if mod_name not in instantiated:
            if d.show_intros:
                segments[key].show_intro()
            instantiated.append(mod_name)
    return segments


def parse_seg_key_and_fmt(seg):
    # If the segment is just a plain-old string,
    # use that as the key and assume no formatting
    seg_key = ''
    seg_fmt = {}
    if isinstance(seg, str):
        seg_key = seg
    # But if it's a list, use the first element as key
    # and second element (if any) as format stuff
    elif isinstance(seg, list):
        seg_key = seg[0]
        if len(seg) > 1:
            seg_fmt = seg[1]
    return (seg_key, seg_fmt)
    
    
def show_title(d):
    os.system('clear')
    for i in range(24):
        print()
    d.print(f'RETROFEED - VERSION {VERSION}')
    d.print('Copyright (c) 2023 Jeff Jetton')
    d.print('MIT License')
    d.newline()


###############################################################################

def main():

    # TODO: read in config from toml file once Python 3.11 is standard on Pis
    #       Until then, we'll pull it in from a big honkin' global
    config = CONFIG

    check_config_tables(config)

    # Override with faster timings if there are any command-line args at all
    if len(sys.argv) > 1:
        config = override_timings(config)

    # Create Display object from config settings
    # This will be used by all segments
    d = Display(config['display'])

    # Segment modules may display intros on initialization,
    # but we want the main title to come first
    if d.show_intros:
        show_title(d)
    segments = instantiate_segments(config, d)

    # Unpack the playlist
    segment_pause = config['playlist']['segment_pause']
    order = config['playlist']['order']
    
    d.newline()
    d.newline()
    
    # Main loop
    while True:
        
        for seg in order:
            d.newline()
            d.newline()

            (seg_key, seg_fmt) = parse_seg_key_and_fmt(seg)

            if seg_key not in segments:
                d.newline()
                d.print_header(f'Missing Segment "{seg_key}"', '*')
                d.newline(segment_pause)
                continue
            
            # Show the segment, with any special formating
            segments[seg_key].show(seg_fmt)
            
            d.newline()
            d.newline(segment_pause)

        


if __name__ == "__main__":
    main()
