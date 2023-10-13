################################################################################
#
#   Display Class
#
#   - Stores configured display settings (print speeds, verbosity, etc.)
#   - Provides various printing and text processing functions to segments
#
#   Every segment should accept a Display object at initialization and use its
#   functions for all text display, including linefeeds, headers, update
#   messages, and pauses ("beats") within the segment.
#
################################################################################

import random
import textwrap
import time


class Display:
    
    def __init__(self, display_settings):
        # Use sensible defaults if any of the keys are missing
        self._height = display_settings.get('height', 24)
        self._width = display_settings.get('width', 40)
        self._cps = display_settings.get('cps', 20)
        self._print_delay = 1/self._cps
        self._newline_cps = display_settings.get('newline_cps', 100)
        self._newline_delay = 1/self._newline_cps
        self._beat_delay = display_settings.get('beat_seconds', 1)
        self._force_uppercase = display_settings.get('force_uppercase', True)
        self._verbose_updates = display_settings.get('verbose_updates', True)
        self._prefer_24hr_time = display_settings.get('prefer_24hr_time', True)
        
    # Getters, but no setters (to hopefully keep other code from altering display values)
    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def size(self):
        return (self.height, self.width)

    @property
    def cps(self):
        return self._cps

    @property
    def print_delay(self):
        return self._print_delay

    @property
    def newline_cps(self):
        return self._newline_cps

    @property
    def newline_delay(self):
        return self._newline_delay

    @property
    def beat_delay(self):
        return self._beat_delay

    @property
    def force_uppercase(self):
        return self._force_uppercase

    @property
    def verbose_updates(self):
        return self._verbose_updates

    @property
    def prefer_24hr_time(self):
        return self._prefer_24hr_time

    @property
    def show_intros(self):
        return self._show_intros

    def __str__(self):
        s = f'Display: {self.height} Rows, {self.width} Columns, '
        s += f'{self.cps} CPS (Print Delay: {self.print_delay}s), '
        s += f'Newline CPS: {self.newline_cps} '
        s += f'(Newline Delay: {self.newline_delay}s), '
        s += f'Beat Delay: {self.beat_delay}s, '
        s += f'Force Uppercase: {self.force_uppercase}, '
        s += f'Verbose Updates: {self.verbose_updates}, '
        s += f'24hr Time: {self.prefer_24hr_time}'
        s += f'Show Intros: {self.show_intros}'
        return s
        
        
########  Printing methods  ###################################################

    # Wait for n "beats" (default = 1).  Used below--available to segments too
    # Length of one beat is defined at configuration
    def wait_beats(self, n=1):
        if n < 0:
            n = 1
        for i in range(n):
            time.sleep(self.beat_delay)

    # Slooow version of print()
    # Passed strings should usually be mixed case to give the user the option
    # to see them that way if they conifg force_uppercase to be false
    def print(self, s='', end='\n'):
        # Use wrapping if string is longer than display width
        if len(s) > self.width:
            lines = textwrap.wrap(s, self.width)
            for line in lines:
                # Oooh... recursion!
                self.print(line, end=end)
            return
        for c in s:
            if self._force_uppercase:
                c = c.upper()
            print(c, end='', flush=True)
            time.sleep(self.print_delay) 
        print(end, end='', flush=True)
        time.sleep(self.print_delay)

    # Slooow Newline - Print n spaces with pause for an extra "delay"
    # seconds at some random horizontal point
    def newline(self, delay=None):
        # Pick a random position to pause to avoid(?) screen burn-in
        pause_pos = random.randrange(self.width)
        for i in range(self.width):
            print(' ', end='', flush=True)
            time.sleep(self.newline_delay)
            if i == pause_pos and delay is not None:
                time.sleep(delay)
        print(flush=True)
        time.sleep(self.newline_delay)

    # Display the passed string as a segment header, surrounded by markers
    def print_header(self, s, left_marker=' ', right_marker=None):
        if right_marker is None:
            right_marker = left_marker
        s = s.strip()
        if self.force_uppercase:
            s = s.upper()
        num_markers = 0
        if len(s) + 4 < self.width:
            num_markers = int((self.width - 4 - len(s)) / 2)
        self.print(left_marker * num_markers, end='')
        self.print('  ' + s + '  ', end='')
        self.print(right_marker * num_markers, end='')
        self.print()

    # Display passed string as an "updating..." message
    def print_update_msg(self, m):
        if self.verbose_updates:
            self.print(f'[{m}', end='')
            for i in range(3):
                self.wait_beats()
                self.print('.', end='')
            self.wait_beats()
            self.print(']')
            self.newline()


########  Formatting helpers  #################################################

    # Returns a string for the time given by datetime object dt
    def fmt_time_text(self, dt, use24=None):
        if use24 is None:
            use24 = self.prefer_24hr_time
        h = dt.hour
        if h > 12 and use24:
            h -= 12
        return str(h) + dt.strftime(":%M%p")


    # Returns a string for the date givcen by datetime object dt
    @classmethod
    def fmt_date_text(cls, dt):
        date_text = dt.strftime("%A, %B ")
        day_num = dt.day
        date_text += str(day_num)
        if day_num in (1, 21, 31):
            date_text += 'st'
        elif day_num in (2, 22):
            date_text += 'nd'
        elif day_num in (3, 23):
            date_text += 'rd'
        else:
            date_text += 'th'
        return date_text


    # Substitute some unicode characters, remove others
    # This also removes returns and strips whitespace at ends
    @classmethod
    def clean_chars(cls, s):
        new_s = ''
        for c in s:
            u = ord(c)
            # Tab = four spaces
            if u == 9:
                new_s += '    '
                continue
            # Fancy puncuation and other special characters
            if u >= 0x2013:
                # Various dashes
                if 0x2013 <= u <= 0x2017:
                    new_s += '-'
                # Double quotes
                elif u == 0x201C or u == 0x201D:
                    new_s += '"'
                # Single quotes
                elif u == 0x2018 or u == 0x2019:
                    new_s += "'"
                # Bullet
                elif u == 0x2022:
                    new_s += "*"
                # Ellipsis...
                elif u == 0x2026:
                    new_s += '...'
                # Copyright and Reg Trmk
                elif u == 0x00A9:
                    new_s += '(c)'
                elif u == 0x00AE:
                    new_s += '(R)'
                # Capital and lowercase tilde-n
                elif u == 0x00D1:
                    news_s += 'N'
                elif u == 0x00F1:
                    news_s += 'n'
            # Any old-school ASCII may pass
            elif (32 <= u <= 126):
                new_s += c   
        return new_s.strip()
    

    # Pulls out a few HTML tags
    @classmethod
    def strip_tags_DEPRECATED(cls, s):
        s = s.replace('\\u003c', '<')
        s = s.replace('\\"', '"')
        s = s.replace('</a>', '')
        while True:
            start_pos = s.find('<a')
            if start_pos < 0:
                break
            end_pos = s.find('>', start_pos)
            if end_pos < 0:
                break
            s = s[0:start_pos] + s[end_pos+1:]
        s = s.replace('<br>', '\n')
        s = s.replace('<BR>', '\n')
        return s
            


