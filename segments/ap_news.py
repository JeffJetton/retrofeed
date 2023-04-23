################################################################################
#
#  Associated Press News
#
#  Webscrapes news briefs info from apnews.com
#
#  Can cycle through a total of [max_items] news items, showing [items] news
#  summaries each time, and/or display [items] top headlines.
#
#   - Initialization parameters:
#
#       refresh     Minutes to wait between webscrapes (default=30, min=1).
#
#
#   - Format parameters:
#
#       items       Number of news items or headlines to display during each
#                   call to the segment's show() method.  Default = 3
#
#       max_items   Max items to cycle through over all calls to show().  Once
#                   that many items have been displayed (not counting headline
#                   mode), we'll start back at the top with the first item.
#                   Items also always reset to top when data is refreshed.
#                   Default = 15
#
#       headlines   True/False (default = False).  If true, only headlines are
#                   shown, always starting with the first item and displaying
#                   [items] headlines.  The segment is labeled "headlines"
#                   instead of "summaries".  This does not reset or otherwise
#                   affect the display sequence used with regular (non-headline)
#                   news items.
#
#   Jeff Jetton, Jan-Mar 2023
#
################################################################################



import datetime as dt
import requests
from segment_parent import SegmentParent


class Segment(SegmentParent):

    def __init__(self, display, init):
        super().__init__(display, init, default_refresh=30)


    def show_intro(self):
        self.d.print('News from apnews.com')


    def get_headline(self, s):
        pos = s.find('"headline":')
        if pos < 0:
            return None
        pos += 12
        s = s[pos:]
        pos = s.find('"description":')
        if pos < 0:
            return None
        pos -= 2
        s = s[0:pos]
        return self.d.strip_tags(self.d.clean_chars(s))


    def get_summary(self, s):
        pos = s.find("\\u003c/p>")
        if pos < 0 or pos >= 500:
            return None
        pos -= 0
        s = s[9:pos]
        return self.d.strip_tags(self.d.clean_chars(s))
    
    
    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     'item_index':0,
                     'items':[],
                    }
        url = 'https://apnews.com'
        # We won't use BeautifulSoup -- Just munge the source directly
        response = requests.get(url, headers={'Cache-Control': 'no-cache'})
        if response.status_code == 200:
            split_source = response.text.split('"firstWords":')
            for chunk in split_source:
                headline = self.get_headline(chunk)
                summary = self.get_summary(chunk)
                if headline is not None and summary is not None and headline.lower().find('top stories ') < 0:
                    self.data['items'].append({'headline':headline, 'summary':summary})
        if len(self.data['items']) == 0:
            self.data['items'].append({'headline':'*** Newsfeed Unavailable ***', 'summary':'N/A'})




    def show(self, fmt):
        items = fmt.get('items', 3)
        max_items = fmt.get('max_items', 15)
        headlines = fmt.get('headlines', False)
        
        # Refresh?
        if self.data_is_stale():
            self.d.print_update_msg('Getting Latest News')
            self.refresh_data()

        # Show header and set up start and end indices, based on headlines
        if headlines:
            self.d.print_header('AP News Headlines', '!')
            # Headlines always start with first item. They don't cycle.
            start_index = 0
            end_index = min(items, len(self.data['items']))
        else:
            self.d.print_header('AP News Summaries', '!')
            # Restart item index?
            if self.data['item_index'] >= max_items or self.data['item_index'] >= len(self.data['items']):
                self.data['item_index'] = 0
            start_index = self.data['item_index']
            end_index = min(start_index + items, len(self.data['items']))

        # Show items
        for item in self.data['items'][start_index:end_index]:
            if not headlines:
                self.d.newline()
            self.d.newline(self.d.beat_delay)
            self.d.print(item['headline'])
            if not headlines:
                self.d.newline()
                self.d.print(item['summary'])
                self.data['item_index'] += 1




