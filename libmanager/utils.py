#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):

import pathlib

def measure_disk_space(path):
    # Report the disk space du -hs style for a directory
    KB = 1024
    b = sum(file.stat().st_size for file in pathlib.Path(path).rglob('*'))
    k = b / KB**1
    m = k / KB**1
    g = m / KB**1
    return f'{k:.2}kb', f'{m:.2}Mb', f'{g:.2}Gb'
