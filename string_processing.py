# Substitute some unicode characters, remove others
# This also removes returns and strips whitespace at ends
def clean_chars(s):
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
def strip_tags(s):
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
            

# Given a datetime object, return formatted time
# (no zero padding for one-digit hours)
def format_time(dt):
    h = dt.hour
    if h > 12:
        h -= 12
    return str(h) + dt.strftime(":%M%p")

