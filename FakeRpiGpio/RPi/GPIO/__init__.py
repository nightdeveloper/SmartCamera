BOARD = 1
OUT = 2
IN = 3


def setmode(a):
    print "set mode " + a


def setup(a, b):
    print "setup " + a + ", " + b


def output(a, b):
    print "output " + a


def cleanup():
    print "cleanup"


def setwarnings(flag):
    print 'setwarnings ' + flag
