import logging
from os.path import join
from os.path import dirname

# The background is set with 40 plus the number of the color, and the foreground with 30
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
# Levelname to color
COLORS = {'WARNING': YELLOW, 'INFO': WHITE, 'DEBUG': BLUE, 'CRITICAL': YELLOW, 'ERROR': RED}
# FORMAT='[%(asctime)s %(levelname)s]%(filename)s:%(lineno)s - %(message)s')
FORMAT = "[%(asctime)s][%(levelname)-18s]$BOLD%(filename)s$RESET:%(lineno)d %(message)s "


def init():
    colorFormatter = ColoredFormatter(formatterMessage(FORMAT))
    plainFormatter = ColoredFormatter(formatterMessage(FORMAT), useColor=False)
    console = logging.StreamHandler()
    console.setFormatter(colorFormatter)
    fileHandler = logging.FileHandler('./app.log', 'w')
    fileHandler.setFormatter(plainFormatter)
    rootLogger = logging.getLogger()
    rootLogger.addHandler(console)
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(logging.DEBUG)
    logging.info("Logging is configured in {}".format(__file__))


def formatterMessage(message, useColor=True):
    if useColor:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, useColor=True):
        logging.Formatter.__init__(self, msg)
        self.useColor = useColor

    def format(self, record):
        levelname = record.levelname
        if self.useColor and levelname in COLORS:
            levelnameColor = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelnameColor
        return logging.Formatter.format(self, record)
