__author__ = 'mwitas'

from mininet.topo import Topo
from mininet.net import Mininet


class DmasTopo(Topo):

    def __init__(self):
        Topo.__init__(self)
        self.net = None

    def get_net(self, **kwargs):
        if self.net is None:
            self.net = Mininet(self, **kwargs)

        return self.net
