################################################################################
#
#   Lucky Numbers
#
#   Very basic example of a segment class
#
#   - Takes no initialization, takes no formatting
#   - Creates a series of pseudorandom numbers based on the computer's MAC
#     address and the current local date, so you get the same lucky numbers
#     everytime you use this on a given day, but usually different from numbers
#     other people might get that day on their own Pi
#   - The numbers are picked to be compatible with the rules of both Powerball
#     and MegaMillions lotteries in the U.S., in case you want to risk a few
#     dollars.  (But of course they're completely random and have no better
#     chance of winning than any other set of numbers, so good luck with that.)
#
#   Jeff Jetton, February 2023
#
################################################################################

import datetime as dt
import random
from segment_parent import SegmentParent
import uuid


# Class name should always be "Segment" and should always inherit SegmentParent
class Segment(SegmentParent):
    
    def __init__(self, display, init):
        # All segment initializers must take a reference to a Display object
        # first, and then an optional dictionary containing any initialization parameters
        # In this case, we're not using any initialization parameters, so we ignore init.
        # (But we still have to have the parameter for it in the method declaration!)
        # SegmentParent provides a useful __init__, but since we're not storing
        # any persistent data, we don't even need to use that.
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
        self.d.print('Disclaimer: Luckiness of Lucky Numbers is not guaranteed')


    def get_lucky_numbers(self):
        # Get the number of days since Jan 1, 1970 (local)
        days = (dt.datetime.now() - dt.datetime(1970,1,1)).days
        # Get MAC address
        mac = uuid.getnode()
        # Build today's seed from those two things
        seed = (days * mac) & 0xFFFF
        random.seed(seed)
        # Six numbers from 1 to 69
        nums = random.sample(range(1,70), 6)
        # If the last number is over 25 or matches one of the others,
        # keep picking news ones until it's not
        while nums[5] > 25 or nums[5] in nums[0:5]:
            nums[5] = random.randint(1, 25)
        # Put first five numbers in order
        sorted = nums[0:5]
        sorted.sort()
        sorted.append(nums[5])
        return sorted


    def show(self, fmt):
        # All segments must have a show() method, which is called by
        # retrofeed.py when the segment comes up next in the playlist.
        # We're not providing any special formatting options, so we ignore fmt
        nums = self.get_lucky_numbers()
        self.d.print("Your Lucky Numbers for Today:")
        self.d.print('  ', end='')
        for i, num in enumerate(nums):
            self.d.print(f'{num} ', end='')
            if i == 4:
                # Build suspense!
                self.d.print('and', end='')
                for j in range(3):
                    self.d.wait_beats()
                    self.d.print('.', end='')
                self.d.wait_beats()
                self.d.print(' ', end='')
        self.d.newline()


