from topo.dmastopo import DmasTopo

__author__ = 'mwitas'

from mininet.topo import Topo


class ControllerTopo:

    def __init__(self, topo):
        """
        :type topo: DmasTopo
        """

        topo.net.addController('c0')
