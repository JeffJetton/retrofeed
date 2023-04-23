################################################################################
#
#   Wikipedia "On This Day" Segment
#
#   Basic framework for making a segment that fetches and persistently stores
#   information, then displays it
#
#   - Initialization parameters:
#
#       refresh     Minutes to wait between data fetches (default=120)
#
#   - Format parameters:  none
#
#
#   Jeff Jetton, April 2023
#
################################################################################

from bs4 import BeautifulSoup
import datetime as dt
import requests
from segment_parent import SegmentParent


class Segment(SegmentParent):
    
    def __init__(self, display, init):
        super().__init__(display, init)
       

    def show_intro(self):
        # No intro
        return



    def parse_list(self, lst):
        list_items = lst.find_all('li')
        for list_item in list_items:
            list_item = self.d.strip_tags(list_item.text)
            list_item = list_item.replace(' (pictured)', '')
            list_item = list_item.replace(' (depicted)', '')
            self.data['items'].append(list_item)



    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     'item_index':0,
                     'items':[]
                    }
        today = dt.date.today()
        # For debugging...
        #today = dt.date(2023, 3, 11)
        # Format as full month plus day-of-month w/o leading zero
        self.data['today'] = today.strftime('%B %d').replace(' 0', ' ')
        url = 'https://en.wikipedia.org/wiki/Wikipedia:Selected_anniversaries/'
        today_formatted = self.data['today'].replace(' ', '_')
        url += today_formatted
        # Get raw source first
        response = requests.get(url, headers={'Cache-Control': 'no-cache'})
        if response.status_code != 200:
            return
        # Split it on "today" page links
        link = f"<a href=\"/wiki/{today_formatted}\" title=\"{self.data['today']}\">{self.data['today']}</a>"
        # Get each list found in the third chunk
        soup = BeautifulSoup(response.text.split(link)[2], 'html.parser')
        lists = soup.find_all('ul')
        # First list only, for now (the birth/death list often has obscure names)
        self.parse_list(lists[0])



    def show(self, fmt):
        # How many OTD items should we show at a time?
        items_to_show = fmt.get('items', 1)
        if items_to_show < 0:
            items_to_show = 1
        # Refresh if needed
        if self.data_is_stale():
            self.d.print_update_msg('Consulting Wikipedia')
            self.refresh_data()
        # Header
        self.d.print_header(self.data['today'] + ': On This Day', '-')
        self.d.newline()
        # No items fetched for some weird reason?
        if len(self.data['items']) == 0:
            self.d.print('No "On This Day" data available')
            self.d.newline(self.d.beat_delay)
            return
        # Show requested number of items
        items_shown = 0
        while items_shown < items_to_show:
            self.d.print(self.data['items'][self.data['item_index']])
            self.d.newline(self.d.beat_delay)
            self.data['item_index'] += 1
            if self.data['item_index'] >= len(self.data['items']):
                self.data['item_index'] = 0
            items_shown += 1

        

