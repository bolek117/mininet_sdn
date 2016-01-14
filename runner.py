#!/usr/bin/env python

__author__ = 'mwitas'

from argparse import ArgumentParser
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
import mininet.log
from topo.pox import POX
from topo.simpletopo import SimpleTopo


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-s', '--switches', type=int, default=1, dest='no_of_switches',
                        help='Sets number of the switches in chain HOST_1 <-> Switch_1 <-> ... <-> Switch_N <-> HOST_2')

    return parser.parse_args()


if __name__ == '__main__':
    mininet.log.setLogLevel('info')

    args = parse_args()

    simple_topo = SimpleTopo(args.no_of_switches)
    # net = Mininet(topo=simple_topo, controller=POX('c2', script='spam_class'))
    net = Mininet(topo=simple_topo, controller=RemoteController('c0'))

    net.start()
    CLI(net)
    net.stop()
