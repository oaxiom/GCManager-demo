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

def obfuscate_name(name):
    obf_name = []
    for n in name.split(' '):
        obf_name.append(f'{n[0]}*{n[-1]}')
    return ' '.join(obf_name)

if __name__ == '__main__':
    print(obfuscate_name('王老师'))
    print(obfuscate_name('John Smith'))