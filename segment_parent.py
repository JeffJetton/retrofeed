################################################################################
#
#   Segment Parent Class
#
#   All Segment classes should inherit from this parent class to ensure
#   required methods are implemented.
#
#   The provided methods are handy too:
#
#     __init__():     Takes care of most standard instantiation tasks
#                     Call as super().__init__(display, init)
#
#     data_is_stale:  Returns boolean indicating whether you need a refresh
#
#     get_soup:       Returns a BeautifulSoup object from a url
#
#
#   Jeff Jetton, April 2023
#
################################################################################


from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import datetime as dt
import requests



class SegmentParent(ABC):
    
    def __init__(self, display, init, default_refresh=60):
        # Remember reference to main Display object, using "d" for brevity
        self.d = display
        # Assign refresh time (or use default if none found)
        ref = init.get('refresh', default_refresh)
        if ref < 1:
            ref = 1
        self.refresh = dt.timedelta(minutes=ref)
        # Fetched data is eventually encapsulated into the 'data' instance
        # variable.  For now, we'll set it to None to indicate that we haven't
        # done any fetching yet...
        self.data = None


    def data_is_stale(self):
        # Returns whether or not we need to refresh the data.
        # Depends on 'data', if it is not None, having a 'fetched_on' value
        # representing the datetime of most-recent refresh.
        return self.data is None or dt.datetime.now() - self.data['fetched_on'] >= self.refresh


    def get_soup(self, url):
        # Returns a parsed BeautifulSoup object from passed url, or None
        # if the HTTP request fails
        response = requests.get(url, headers={'Cache-Control': 'no-cache'})
        if response.status_code != 200:
            return None
        return BeautifulSoup(response.text, 'html.parser')


    @abstractmethod
    def show_intro(self):
        # Display credits, disclaimers, etc.  Should always be overridden,
        # even if you don't want to display anything.
        # Called when main program instantiates a particular segment, and
        # only if the show_intros Display setting is True.  If a segment is
        # defined multiple times, such as having a us_weather.py segment for
        # several different cities, this only gets called for the first one.
        pass


    @abstractmethod
    def show(self, fmt):
        # Called by the main program when it's the segment's turn to display
        # A format object is always passed, although it will be None if no
        # formatting is specified in the config object.
        # Typically, the child class will first call data_is_stale() and
        # refresh the data if needed, prior to showing anything.
        pass
        

