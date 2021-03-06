__author__ = 'mwitas'

from topo.dmastopo import DmasTopo


class SimpleTopo(DmasTopo):

    def __init__(self, no_of_switches):
        DmasTopo.__init__(self)

        self.no_of_switches = no_of_switches

        # Add first and last host
        hosts = [self.addHost('h1'), self.addHost('h2')]

        # Switches list initialization
        switches = []
        last_switch = None

        # Add `noOfSwitches` to switches list
        for i in xrange(no_of_switches):
            name = str.format('s{}', i+1)
            e = self.addSwitch(name)
            switches.append(e)

            # Remember actual switch as last added
            last_switch = e

        # Create link between first host and first switch
        self.addLink(hosts[0], switches[0])

        # Create link between last switch and second host
        self.addLink(last_switch, hosts[1])

        # Connect all switches in line
        for i in xrange(no_of_switches-1):
            self.addLink(switches[i], switches[i+1])


def SimpleNet(switches=1, **kwargs):
    topo = SimpleTopo(switches)
    return topo.get_net(**kwargs)
