__author__ = 'mwitas'

from mininet.node import Controller
from os import environ

POXDIR = environ['HOME'] + '/pox'


class POX(Controller):
    def __init__(self, name, cdir=POXDIR, command='python pox.py',
                 cargs='openflow.of_01 --port=%s', **kwargs):
        if 'script' in kwargs:
            cargs += ' ' + kwargs['script']
        else:
            cargs += ' forwarding.l2_learning'

        Controller.__init__(self, name, cdir=cdir, command=command, cargs=cargs, **kwargs)


controllers = {'pox': POX}
