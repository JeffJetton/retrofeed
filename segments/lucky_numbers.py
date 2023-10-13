################################################################################
#
#   Lucky Numbers
#
#   Very basic example of a segment class
#
#   - Takes no initialization, takes no formatting
#   - Creates a series of pseudorandom numbers based on the computer's MAC
#     address and the current local date, so you get the same lucky numbers
#     each time you use this on a given day, but usually different from numbers
#     other people might get that day on their own computer.
#
#   ***  Disclaimer: Luckiness of Lucky Numbers is Not Guaranteed!  :-)
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
        # All segments MUST have a show() method, which is called by
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


