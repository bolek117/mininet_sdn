#!/usr/bin/env python

from argparse import ArgumentParser
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
from topo.pox import POX
from topo.simpletopo import SimpleTopo


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-s', '--switches', type=int, default=1, dest='no_of_switches',
                        help='Sets number of the switches in chain HOST_1 <-> Switch_1 <-> ... <-> Switch_N <-> HOST_2')
    parser.add_argument('-c', '--controller', type=str, default=None, dest='controller_name',
                        help='Name of POX controller to run as default. If not provided, topology will wait for remote controller on port 6633')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    simple_topo = SimpleTopo(args.no_of_switches)

    if args.controller_name is None:
        net = Mininet(topo=simple_topo, controller=RemoteController('c0'))
    else:
        net = Mininet(topo=simple_topo, controller=POX(args.controller_name))

    net.start()
    cli = CLI(net)
    net.stop()
