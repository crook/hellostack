#-*- coding: utf-8 -*-

import logging


def setup_logger(filename, level=logging.INFO):
    # set up logging to file - see previous section for more details
    # logging.basicConfig(
    #    level=logging.DEBUG,
    #  format='%(asctime)s %(name)-8s %(lineno)d %(levelname)-8s %(message)s',
    #    datefmt='%m-%d %H:%M',
    #    filename=filename,
    #    filemode='w+')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(
        '%(asctime)s %(name)-8s %(lineno)d: %(levelname)-8s %(message)s'
    )
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def _s(args):
    """convert anything to string"""
    if isinstance(args, (list)):
        return map(lambda e: str(e), args)
    if isinstance(args, tuple):
        return tuple(map(lambda e: str(e), args))
    else:
        return str(args)


def _f(args):
    """try to convert anything to float"""
    if args == "":
        return "0"

    if isinstance(args, (list)):
        return map(lambda e: float(e), args)
    if isinstance(args, tuple):
        return tuple(map(lambda e: float(e), args))
    else:
        return float(args)


def _u(s, encoding):
    '''convert string to unicode'''
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, encoding)
