#!/usr/bin/env python3
#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os
import argparse, logging

# TODO: Need to make the patient_id log persistant across runs;

sys.path.append('../')
from libmanager import libmanager, VERSION

valid_modes = {
    'patient_exists': 'Check if patient exists, by patient_id',
    # Analysis modes
    'setup': 'Setup new patient',
    'copy': 'Copy sequence data from one location to the patient data location',
    'start': 'Start the analysis (and validate the data looks good)',
    'analyze': 'Analyse data (really report the current progress)',
    # Reporting modes
    'report': 'Generate and retrive a report for a particular disease',
    'summary_statistics': 'Patient_id metadata and results from the sequence data analysis',
    # Accessory modes
    'log_analysis': 'Return the current log data for the analysis.',
    'log_error': 'If an error, return the current log data.',
    # System management
    'clean_free_space': 'Tidy up non-required files'
    }

# Command-line options;
def prepare_parser():
    exmp = 'Example usage: GCmanager -m <verb> -p <patient_id> -s <seq_id>'
    description = 'GCmanager, back end controller'
    parser = argparse.ArgumentParser(prog='GCmanager', description=description, epilog=exmp)

    optional = parser._action_groups.pop()
    optional.add_argument('-s', '--seq_id', required=False, help='Sequence ID number')
    optional.add_argument('-d', '--diseasecode', required=False, help='Disease code number')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-m', '--mode', required=True, help='Mode to use, valid modes: {0}'.format(valid_modes))
    required.add_argument('-p', '--patient_id', required=True, help='Patient ID')

    parser._action_groups.append(optional)

    return parser

def prepare_logging(patient_id:str = None):
    logging.basicConfig(level=logging.DEBUG,
        format='%(levelname)-8s: %(message)s',
        datefmt='%m-%d %H:%M')

    return logging.getLogger(f'GCmanager {patient_id}')


def main(man, args):
    if args.mode == 'patient_exists':
        return man.patient_exists(args.patient_id)

    elif args.mode == 'setup':
        return man.setup(args.patient_id, args.seq_id)

    elif args.mode == 'copy':
        pass

    elif args.mode == 'start':
        pass

    elif args.mode == 'analyze':
        pass

    elif args.mode == 'report':
        assert args.diseasecode, 'diseascode must be specified'
        # TODO: Check the disease code is in the DB.
        return man.generate_report(patient_id, args.diseasecode)

    elif args.mode == 'summary_statistics':
        return man.summary_statistics(args.patient_id)

    elif args.mode == 'log_analysis':
        pass

    elif args.mode == 'log_error':
        pass

    else:
        log.error(f'-m mode {args.mode} not found')
        sys.exit(f'-m mode {args.mode} not found')

    return 0

if __name__ == '__main__':
    script_path = os.path.dirname(os.path.realpath(__file__))

    parser = prepare_parser()
    args = parser.parse_args()

    log = prepare_logging()
    parser.log = log

    home_path = os.path.expanduser('~/GC/') # Production
    if 'demo' in VERSION:
        home_path = os.path.join(script_path, '..', 'GC_demo') # Demo data

    if not os.path.exists(home_path):
        log.error(f"Panic! Data path {home_path} is missing")
        sys.exit(-1)

    man = libmanager.libmanager(log=log, home_path=home_path)

    if args.patient_id:
        # Run patient_exists
        if man.patient_exists(args.patient_id):
            # Swap the logger into the patient_exists directory for persistent logging
            pass

    log.info(f'GCManager {VERSION}')
    log.info('Copyright 2024 Helixiome, all rights reserved')
    log.info('Copyright 2024 ')
    log.info(f'Args: {args}')

    man._security_check()

    res = main(man, args)

    log.info('##### Result packet:')
    print(res)

    # Send the data to the Viewer. Best way to interface with external code?
    # TODO: Send to viewer
