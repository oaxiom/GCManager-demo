
import logging

def prepare_logging():
    logging.basicConfig(level=logging.DEBUG,
        format='%(levelname)-8s: %(message)s',
        datefmt='%m-%d %H:%M')

    return logging.getLogger(f'GCmanager')
