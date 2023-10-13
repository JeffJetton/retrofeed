################################################################################
#
#  Associated Press News
#
#  Webscrapes news briefs from apnews.com
#
#  Can cycle through a total of [max_items] news items, showing the first
#  [item_length] paragraphs of [items] news stories each time, and/or display
#  the top [items] headlines.
#
#   - Initialization parameters:
#
#       refresh     Minutes to wait between webscrapes (default=30, min=1)
#
#       max_items   Number of articles to try to pull down with each refresh
#                   (default=15, min=1, max=30)
#
#
#   - Format parameters:
#
#       items           Number of news stories or headlines to display during
#                       each call to the show() method.  Defaults to 3, or to
#                       [max_items] if in headline mode.
#
#       item_length     Number of paragraphs to display for each story in
#                       normal (non-headline) mode.  (default=2, min=1, max=10)
#
#       headline_mode   true/false (default = false).  If true, only headlines 
#                       are shown, always starting with the first item and
#                       displaying [items] headlines.  The segment is labeled
#                       "AP News Headlines" instead of just "AP News".  This
#                       does not reset or otherwise affect the display sequence
#                       used with regular (non-headline) news items.
#
#
#   Jeff Jetton, Jan-Mar 2023
#   Major updates Oct 20223
#
################################################################################


import datetime as dt
from segment_parent import SegmentParent


INTRO = 'News from apnews.com'


class Segment(SegmentParent):


    def __init__(self, display, init):
        super().__init__(display, init, default_refresh=30, default_intro=INTRO)
        max_items = init.get('max_items', 15)
        self.max_items = self.clamp(max_items, 1, 30)


    def get_story(self, url):
        soup = self.get_soup(url)
        if soup is None:
            return None
        story_div = soup.find('div', 'RichTextStoryBody')
        if story_div is None:
            return None
        story = story_div.find_all('p')
        if story is None or len(story) == 0:
            return None
        story = [self.d.clean_chars(p.get_text()) for p in story]
        return story
    
    
    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     'item_index':0,
                     'items':[],
                    }
        url = 'https://apnews.com/hub/ap-top-news'
        soup = self.get_soup(url)
        if soup is None:
            return
        # Get divs of interest, up to max_items
        story_divs = soup.find_all('div', 'PagePromo-content', limit=self.max_items)
        # Get the urls and titles/headlines from those divs
        for story in story_divs:
            url_obj = story.find('a', 'Link')
            url = url_obj.get('href')
            headline = url_obj.get_text()
            if url is not None and headline is not None:
                headline = self.d.clean_chars(headline)
                self.data['items'].append({'headline':headline, 'url':url})
        # Try to get full stories for the linked articles
        for item in self.data['items']:
            item['story'] = self.get_story(item['url'])
        # Add a special "item" if no items were found
        if len(self.data['items']) == 0:
            self.data['items'].append({'headline':'*** Newsfeed Unavailable ***', 'story':None, 'url':None})


    def show_stories(self, num_items, item_length):
        self.d.print_header('AP News', '!')
        self.d.newline()
        for i in range(num_items):
            self.d.newline(self.d.beat_delay)
            if item_length > 1 and i > 0:
                self.d.newline()
            item = self.data['items'][self.data['item_index']]
            if item['story'] is None or len(item['story']) == 0:
                self.d.print('*** Item Story Unavailable ***')
            else:
                paragraphs = min(item_length, len(item['story']))
                for i in range(paragraphs):
                    self.d.print(item['story'][i])
                    self.d.newline()
            self.data['item_index'] += 1
            if self.data['item_index'] >= len(self.data['items']):
                self.data['item_index'] = 0


    def show_headlines(self, num_headlines):
        self.d.print_header('AP Top Headlines', '!')
        for i, item in enumerate(self.data['items']):
            if i >= num_headlines:
                break
            self.d.newline(self.d.beat_delay)
            self.d.print(item['headline'])


    def show(self, fmt):

        headline_mode = fmt.get('headline_mode', False)
        
        # Refresh?
        if self.data_is_stale():
            self.d.print_update_msg('Getting Latest News')
            self.refresh_data()

        if headline_mode:
            num_items = fmt.get('items', self.max_items)
            self.show_headlines(num_items)
        else:
            num_items = fmt.get('items', 3)
            item_length = fmt.get('item_length', 1)
            item_length = self.clamp(item_length, 1, 10)
            self.show_stories(num_items, item_length)


