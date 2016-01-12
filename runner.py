#!/usr/bin/env python

from topo.simpletopo import SimpleNet
from argparse import ArgumentParser

import mininet.cli


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-s', '--switches', type=int, default=1, dest='no_of_switches',
                        help='Sets number of the switches in chain HOST_1 <-> Switch_1 <-> ... <-> Switch_N <-> HOST_2')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    net = SimpleNet(args.no_of_switches)

    net.start()
    cli = mininet.cli.CLI(net)
    net.stop()
