
# Artificially restring gcms to a single disease, to emulate

import sys, os

# To restrict you just add the disease key to the 'rest' key

# I might worry that these IDs are not stable...
# I think it doen't matter.

# Pharma is P1-P38
# Risk is R1-R43

# The restrictions are always either None (i.e. all) or a whitelist.

sys.path.append('../../')

from libmanager import gcms, logger

g = gcms.gcm_file('SRR10286930.data.gcm', logger.basic_logger())
g.rest = ['R1', 'R2', 'P1', 'P2']
g.save('SRR10286930.restricted1.data.gcm')

g = gcms.gcm_file('SRR10286930.data.gcm', logger.basic_logger())
g.rest = [f'R{i}' for i in range(50)]
g.save('SRR10286930.restricted.Riskonly.data.gcm')

g = gcms.gcm_file('SRR10286930.data.gcm', logger.basic_logger())
g.rest = [f'P{i}' for i in range(50)]
g.save('SRR10286930.restricted1.Pharmaonly.data.gcm')


