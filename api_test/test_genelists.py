#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os
sys.path.append('../')
from libmanager import tinyglbase, logger

log = logger.basic_logger()

# These functions are confirmed to have a use somewhere in GCmanager

alist = [
    {'name': 'A'},
    {'name': 'B'},
    {'name': 'C'}
    ]

blist = [
    {'name': 'A'},
    {'name': 'D'},
    {'name': 'E'},
    {'name': 'E'},
    ]


# genelist()
a = tinyglbase.genelist(format=True, log=log)
b = tinyglbase.genelist(format=True, log=log)

# load_list()
a.load_list(alist)
b.load_list(blist)

# .saveTSV()
a.saveTSV('alist.tsv')
b.saveTSV('blist.tsv')

# .save()
a.save('alist.glb')
b.save('blist.glb')

# .sort()
a.sort('name')
b.sort('name')

# .removeDuplicates()
a = a.removeDuplicates('name')
b = b.removeDuplicates('name')

# .map()
o = a.map(genelist=b, key='name')

