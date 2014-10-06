#/usr/bin/env python2

import logging,sys

class LogFormatter(logging.Formatter):
    FORMATS = {logging.DEBUG :"DEBUG: %(lineno)d: %(message)s",
               logging.ERROR : "ERROR: %(message)s",
               logging.INFO : "%(message)s",
               'DEFAULT' : "%(levelname)s: %(message)s"}

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)

hdlr = logging.StreamHandler(sys.stderr)
hdlr.setFormatter(LogFormatter())
logging.root.addHandler(hdlr)
logging.root.setLevel(logging.INFO)

