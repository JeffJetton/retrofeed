################################################################################
#
#   Date Time Segment 
#
#   - Basic example of a segment class
#   - Only overrides the required show() method
#   - Takes no initialization parameters, but does allow for a few formats
#
#   Jeff Jetton, Jan-Feb 2023
#
################################################################################

import datetime as dt
from segment_parent import SegmentParent


# Class name should always be "Segment" and inherit from SegmentParent
class Segment(SegmentParent):

    def show(self, fmt):
        # All segments must have a show() method, which is called by
        # retrofeed.py when the segment comes up next in the playlist
        #    - Method will be passed a dictionary of formatting parameters
        #    - Even if no formatting requested or needed, it will still
        #      get an empty dictionary
        #    - The expected keys may not exist, nor might they have expected
        #      values if they do... be careful!

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

