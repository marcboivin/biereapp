import logging
from biereapp import settings

if __name__ == '__main__':
    def logit(what):
        print "logit: " + what
        print settings.DEBUG
        if settings.DEBUG:
            logging.debug(what)
        
    def setup_logging():
        # Setup debugging
        LOG_FILENAME = 'debug.log'
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)