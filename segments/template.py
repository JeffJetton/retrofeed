################################################################################
#
#   Segment Template
#
#   Basic framework for making a segment that fetches and persistently stores
#   information, then displays it
#
#   - Initialization parameters (all optional)
#
#       refresh     Minutes to wait between data fetches (default=60, minimum=1)
#       intro       Text to display when segment is instantiated
#
#   - Format parameters:  none
#
#
#   Jeff Jetton, March-April 2023
#
################################################################################

import datetime as dt
from segment_parent import SegmentParent


class Segment(SegmentParent):
    
    def __init__(self, display, init):
        # Call parent, which stores the display object as 'd', sets up the
        # refresh time and intro from init (or uses defaults), and creates
        # an empty 'data' variable, set to None for the time being.
        super().__init__(display, init)
        # Other things this segment needs to do (set up additional init
        # parameters, for example) go here.
        # If it doesn't need to do anything else, and if we don't need
        # to override SegmentParent's default refresh time or intro,
        # then this whole __init__ contructor function can be removed.


    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     }
        # Do fetching here (webscraping, RSS, API, file read, etc.)
        # For now, we'll just assign a string constant and imagine we did
        # something fancier...
        self.data['message'] = 'hello, world'



    def show(self, fmt):
        # Refresh if needed
        if self.data_is_stale():
            self.d.print_update_msg('Updating Data')
            self.refresh_data()

        self.d.print_header('Template', '=')
        self.d.newline()

        self.d.print(self.data['message'])
        self.d.newline()


