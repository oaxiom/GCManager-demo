
import sys, os, gzip, pickle

if len(sys.argv) != 2:
    print('Incorrect number of arguments. should be PID file only')
    sys.exit(-1)

print('Starting to make GCM')

PID = sys.argv[1]

gcm_data = {
    'qc': None,
    'full_logs': None,
    'pharma': None,
    'risk': None,
    'clinvar': None, # Not currently used.
    'rest': None,
    }

# reverse is gzip.decompress(bytes_obj).decode()

# QC
with open(f'{PID}.qc', 'rt') as f:
    gcm_data['qc'] = f.read()

# Full logs
with open('full_logs.out.gz', 'rb') as f:
    gcm_data['full_logs'] = f.read()

# pharma table
with open(f'{PID}.pharmagkb.txt', 'rt') as f:
    gcm_data['pharma'] = gzip.compress(f.read().encode())

# risk
with open(f'{PID}.risk.txt', 'rt') as f:
    gcm_data['risk'] = gzip.compress(f.read().encode())

# clinvar
with open(f'{PID}.clinvar.pathogenic.tsv', 'rt') as f:
    gcm_data['clinvar'] = gzip.compress(f.read().encode())

# save the gcm
with open(f'{PID}.data.gcm', "wb") as oh:
    pickle.dump(gcm_data, oh, -1)

print('Finsihed making GCM')
