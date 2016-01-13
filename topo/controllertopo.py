from topo.dmastopo import DmasTopo

__author__ = 'mwitas'


class ControllerTopo(DmasTopo):

    def __init__(self, topo):
        """
        :type topo: DmasTopo
        """
        DmasTopo.__init__(self)
        self.base_topo = topo
        net = self.get_net()
        # net.addController('c0')

    def get_net(self, **kwargs):
        return self.base_topo.get_net(**kwargs)


def ControllerNet(base_topo, **kwargs):
    topo = ControllerTopo(base_topo)
    return topo.get_net(**kwargs)