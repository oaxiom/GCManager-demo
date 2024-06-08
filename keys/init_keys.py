#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#


from libmanager import security

# Generate DEMO keys. These are committed to the repository.

public_key, private_key = security.gen_keys()
security.store_keys(public_key, private_key, prefix='demo')

# Generate Production keys. Only the PUBLIC is in the repository.

public_key, private_key = security.gen_keys()
security.store_keys(public_key, private_key, prefix='production')

