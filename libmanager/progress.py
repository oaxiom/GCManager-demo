#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

"""

a simple progress bar for some of the longer functions expected to take a long-time.

Inspired from the progress bar in urlgrabber.

"""

import sys

class progressbar:
    def __init__(self, maximum_value, output=sys.stderr):
        """
        Initialise the progress bar

        **Arguments**

            maximum_value (Required)
                the maximum_value to move the bar up to.

            output (Optional, defaults to stderr)
                the output device to use.
        """
        self.maximum = maximum_value
        if maximum_value <= 0: # special case, probably being sent a delayedlist
            self.maximum = -1

        self.__writer = output
        self.__barwidth = 30 # bar_width in characters.
        self.__last_percent = -1 # only print if __last_pecent is incremented.

    def update(self, new_value):
        """
        Update progress meter with new_value

        **Arguments**

            new_value (Required)
                should be some number between 0 .. maximum_value
        """
        if self.maximum == -1:
            return False # disable progress bar in wierd situations

        t_percent_done = int(((new_value+1) / self.maximum) * self.__barwidth)

        if t_percent_done > self.__last_percent:
            percent_done = int(((new_value+1) / self.maximum) * 100)
            done = "".join("=" * t_percent_done)
            self.__writer.write(f"\r[{done:-<30}] {percent_done}% ({new_value+1:,}/{self.maximum:,})")
            self.__last_percent = t_percent_done

        if new_value+1 >= self.maximum: # if the last line, reset the console so the result overprints the progress bar.
            self.__writer.write("\r") # pad out to overwrite the previous bar.
            self.__writer.write("\r                                                        ") # pad out to overwrite the previous bar.
            self.__writer.write("\r") # pad out to overwrite the previous bar.


