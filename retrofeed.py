################################################################################
#
#   retrofeed.py - Main entry point for running RetroFeed
#
#   - Reads in config.toml
#   - Instantiates Display and Segment objects based on the config file
#   - Cycles through the Segments and asks them to send info to standard output
#     (via Display), in the order/manner specified in the config file
#
#   The initial use was to set up a Rasperry Pi to output the text to a CRT
#   over the composite output, but of course you can use any terminal-type
#   output/display solution.
#
#   Jeff Jetton
#
#   January-October 2023
#
################################################################################


# TODO: Wikipedia should remove (Example pictured) and other photo references
#       and be case-insensitive when doing so
# TODO: Add library requirements to README


# Standard library imports
import datetime as dt
import importlib.util
import os
import sys
import textwrap as tw
import time
import tomllib

# RetroFeed imports
from display import Display



# Globals...
VERSION = '1.0.0'
COPYRIGHT_YEAR = '2023'
CONFIG_FILENAME = 'config.toml'
EXPECTED_TABLES = ['display', 'segments', 'playlist']



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
    # Keep track of intro strings we show, so we don't show any more than once
    shown_intros = []
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
        # If we haven't heard it already, give the module
        # a chance to introduce itself...
        intro = segments[key].intro
        if intro is not None:
            intro = intro.strip()
            if intro != '' and intro not in shown_intros:
                d.print(intro)
                shown_intros.append(intro)
    return segments


def parse_seg_key_and_fmt(seg):
    seg_key = ''
    seg_fmt = {}
    # If the segment is just a plain-old string,
    # use that as the key and assume no formatting
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
    d.print(f'Copyright (c) {COPYRIGHT_YEAR} Jeff Jetton')
    d.print('MIT License')
    d.newline()



###############################################################################

def main():

    # Get config info from the TOML file
    try:
        with open(CONFIG_FILENAME, 'rb') as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        print(f'\n*** Missing configuration file "{CONFIG_FILENAME}"\n')
        return
    check_config_tables(config)

    # Override with faster timings if there are any command-line args at all
    # Handy for quickly checking segments without having to change config.toml
    if len(sys.argv) > 1:
        config = override_timings(config)

    # Create Display object from config settings
    # This will be used by all segments
    d = Display(config['display'])

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
