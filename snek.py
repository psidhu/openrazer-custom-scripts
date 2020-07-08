"""Snake on razer keyboards

Copyright (C) 2020  Pushpal Sidhu

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

------------------------------------------------------------------------

This is literally a dumb, automated version of the snake game played
out on razer keyboards. Note that this is really intended for the
Huntsman TE (or any TKL I guess), though I don't see why it wouldn't
work elsewhere.

Though I could (and probably should) modularize the snake class, I
won't.

"""


import random
import time

from openrazer.client import DeviceManager
from openrazer.client import constants as razer_constants

class Snek():
    """
    Snek class. Plays out a dumb version of snake with a snake named
    Snek.
    """

    def __init__(self, min_row, min_col, max_row, max_col):
        """ Snek snek

        @min_row Min row to play in
        @min_col Min col to play in
        @max_row Max row to play in
        @max_col Max col to play in
        """

        self.directions = {
            'UP' : -1,
            'DOWN' : 1,
            'LEFT' : -1,
            'RIGHT' : 1,
        }

        self._min_row = min_row
        self._min_col = min_col
        self._max_row = max_row
        self._max_col = max_col

        # Init snek
        self._snek = [
            [int((self._min_row + self._max_row) / 2), int((self._min_col + self._max_col) / 2)],
            [int((self._min_row + self._max_row) / 2), int((self._min_col + self._max_col) / 2 - 1)],
            [int((self._min_row + self._max_row) / 2), int((self._min_col + self._max_col) / 2 - 2)]
        ]

        # Init snek dir
        self._snek_dir = 'RIGHT'

        # Init apple (I think it's an apple?) to right of snek
        self._apple = [self._min_row, self._min_col]
        self._apple = [self._snek[0][0], self._snek[0][1] + 1]

        # Why not
        self._score = 1

    def __del__(self):
        "R.I.B"
        pass

    def _get_new_coord(self, direction):
        """Get next coordinates

        Return next coordinates dependent on the direction. Note that
        these coordinates are allowed to be out of bounds.
        """

        new_head_coord = [
            self._snek[0][0] + (self.directions[direction] if ('UP' == direction) or ('DOWN' == direction) else 0),
            self._snek[0][1] + (self.directions[direction] if ('LEFT' == direction) or ('RIGHT' == direction) else 0)
        ]

        return new_head_coord

    def _get_adj_coord(self, direction):
        """Get adjusted coordinates

        Return next coordinates, adjusted for wraparound
        """

        coord = self._get_new_coord(direction)
        if coord[0] == self._min_row - 1:
            coord[0] = self._max_row
        if coord[1] == self._min_col - 1:
            coord[1] = self._max_col

        if coord[0] == self._max_row + 1:
            coord[0] = self._min_row
        if coord[1] == self._max_col + 1:
            coord[1] = self._min_col

        return coord

    def get_apple(self):
        """Get Dem Apples"""
        return self._apple

    def get_snek(self):
        """Get snek layout"""
        return self._snek

    def get_score(self):
        """Get current score"""
        return self._score

    def set_dir(self, direction):
        """Force set a direction

        @return 0 on success, else error
        """
        if direction not in self.directions:
            return -1

        self._snek_dir = direction
        return 0

    def set_non_destructive_dir(self, direction):
        """Set direction without eating self

        @return 0 on success, else error
        """

        coord = self._get_adj_coord(direction)
        if coord in self._snek:
            return -1
        self.set_dir(direction)
        return 0

    def set_smart_dir(self):
        """Randomly set direction without eating self"""
        scrambled = list(self.directions)
        random.shuffle(scrambled)
        for key in scrambled:
            if self.set_non_destructive_dir(key):
                continue
            else:
                break

    def incr(self):
        """Increment snek one step

        @return < 0 on error, 0 if increment occurred without
        incident, and > 0 for each apple eaten in step
        """
        self._snek.insert(0, self._get_adj_coord(self._snek_dir))

        # We eat ourself?
        if self._snek[0] in self._snek[1:]:
            return -1

        ret = 0
        if self._snek[0] == self._apple:
            self._score += 1
            ret = 1

            count = 0
            while True:
                apple = [random.randint(self._min_row, self._max_row),
                         random.randint(self._min_col, self._max_col)]
                if apple not in self._snek:
                    break
                else:
                    count += 1
                    max_tiles = (self._max_row - self._min_row) * (self._max_col - self._min_col)
                    if count > max_tiles:
                        return -1

            self._apple = apple
        else:
            self._snek.pop()

        return ret

def main():
    device_manager = DeviceManager()
    devices = device_manager.devices
    for device in devices:
        if not device.fx.advanced:
            print("Skipping device " + device.name + " (" + device.serial + ")")
            devices.remove(device)

    # Disable daemon effect syncing.
    # Without this, the daemon will try to set the lighting effect to every device.
    device_manager.sync_effects = False

    # Use last device found since that's all I have and use on my system...
    device.fx.advanced.matrix.reset()
    device.fx.advanced.draw()

    # Limit snake game to main portion of keyboard
    snek = Snek(1, 2, device.fx.advanced.rows-2, device.fx.advanced.cols-6)
    while True:
        # Draw snek
        head_and_tail = snek.get_snek()
        apple_x, apple_y = snek.get_apple()

        device.fx.advanced.matrix.reset()
        count = 0
        for x,y in head_and_tail:
            if 0 == count:
                device.fx.advanced.matrix[x, y] = (255, 255, 0)
            else:
                device.fx.advanced.matrix[x, y] = (0, 255 / count, 0)
            count += 1

        device.fx.advanced.matrix[apple_x, apple_y] = (255, 0, 0)
        device.fx.advanced.draw()
        time.sleep(1 / snek.get_score())

        # Randomly change dir
        snek.set_smart_dir()
        res = snek.incr()
        if res < 0:
            time.sleep(snek.get_score())
            device.fx.wave(razer_constants.WAVE_RIGHT)
            time.sleep(snek.get_score())
            del snek
            snek = Snek(1, 2, device.fx.advanced.rows-2, device.fx.advanced.cols-6)
        elif res > 0:
            device.fx.static(random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255))
            time.sleep(0.750)
            device.fx.static(random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255))
            time.sleep(0.750)

if __name__ == '__main__':
    main()
