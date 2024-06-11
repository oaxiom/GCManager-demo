#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

import sys
import subprocess
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

def guid():
    def run(cmd):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, check=True, encoding="utf-8").stdout.strip()
        except:
            return None

    if sys.platform == 'darwin':
        return run("ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'",)
    if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'msys':
        return run('wmic csproduct get uuid').split('\n')[2].strip()
    if sys.platform.startswith('linux'):
        return run('cat /var/lib/dbus/machine-id') or run('cat /etc/machine-id')

if __name__ == '__main__':
    print(obfuscate_name('王老师'))
    print(obfuscate_name('John Smith'))

