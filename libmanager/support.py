
import logging

valid_laguages = {
    'EN': 'English',
    'CN': '简体中文',
    }

valid_genome_dbs = {
    'PharmaGKB': 'Drug-genome associations',
    }

def prepare_logging():
    logging.basicConfig(level=logging.DEBUG,
        format='%(levelname)-8s: %(message)s',
        datefmt='%m-%d %H:%M')

    return logging.getLogger(f'GCmanager')
