################################################################################
#
#   Date Time Segment 
#
#   - Basic example of a segment class
#   - Takes no initialization parameters, but does allow for a few formats
#
#   Jeff Jetton, Jan-Feb 2023
#
################################################################################

import datetime as dt
from segment_parent import SegmentParent


# Class name should always be "Segment" and inherit from SegmenParent
class Segment(SegmentParent):
    
    def __init__(self, display, init):
        # All segment initializers must take a reference to a Display object
        # first, and then a dictionary containing any initialization parameters
        #    - Init parameters should apply to the data fetches/calculations
        #      done for the life of this object
        #    - Parameters dealing with formatting the data, which could change
        #      across different showings of the segment, but don't change the
        #      underlying data, should be used with the show() method, not here
        #    - Even if the segment requires no initialization, RetroFeed will
        #      still pass it an empty dictionary, so allow for it!
        #    - The expected keys may or may not be in the init dictionary,
        #      depending on how good a configuration job the user did, so
        #      providing defaults is required
        #    - We're not doing any special initialization... 12hr vs 24hr is a
        #      global preference stored in the Display object
        self.d = display


    def show_intro(self):
        # All segments must have a show_intro() method, which is called just
        # after the segment is instantiated.  You don't have to do anything in
        # this method, but you do have to at least have it.
        #    - It's designed to give the module a chance to display credits,
        #      disclaimers, copyright info, etc.
        #    - It has no parameters other than self
        #    - If the user has configured RetroFeed to create multiple
        #      instances of this segment, show_intro() will only be called
        #      after the first one, so intros display only once per module.
        #    - In this case, we have nothing important to say, so...
        pass


    def show(self, fmt):
        # All segments must have a show() method, which is called by
        # retrofeed.py when the segment comes up next in the playlist
        #    - Method will be passed a dictionary of formatting parameters
        #    - Even if no formatting requested or needed, it will still
        #      get an empty dictionary
        #    - As with __init__(), the expected keys may not exists,
        #      nor might they have expected values if they do... be careful!

        # Always check for missing/wrong format info and provide sensible defaults
        fmt = fmt.get('format', 'long')
        if fmt not in ('long', 'short', 'longdate', 'longtime', 'shortdate', 'shorttime'):
            fmt = 'long'

        now = dt.datetime.now()

        # The Display object comes with some handy date/time formatters
        # By default, fmt_time_text() heeds 12/24hr preference specified
        # in the Display config options
        date_text = self.d.fmt_date_text(now)
        time_text = self.d.fmt_time_text(now)
        date_long = ('It is ' + date_text)
        time_long = ('Current time is ' + time_text)
        
        if fmt == 'long':
            self.d.print(date_long)
        if fmt == 'long' or fmt == 'longtime':
            self.d.print(time_long)
            return
        if fmt == 'short':
            self.d.print(time_text + ', ' + date_text)
            return
        if fmt == 'longdate':
            self.d.print(date_long)
            return
        if fmt == 'shortdate':
            self.d.print(date_text)
            return
        if fmt == 'shorttime':
            self.d.print(time_text)

