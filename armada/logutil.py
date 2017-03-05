
import logging
from logging.handlers import SysLogHandler

LOG = logging.getLogger('armada')
LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
LOG_DATE = '%m-%d %H:%M'

def setup_logging(args):
    '''
    :params args - logging information arguments in cli

    various utilties to support logging
    '''
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT, date_fmt=LOG_DATE)
    handler = SysLogHandler(address='/dev/log')
    syslog_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    handler.setFormatter(syslog_formatter)
    LOG.addHandler(handler)
