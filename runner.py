#!/usr/bin/env python

from topo.simpletopo import SimpleNet
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-s', '--switches', type=int, default=1, dest='no_of_switches')
    parser.add_argument('-c', '--pingCount', type=int, default=1, dest='count')
    args = parser.parse_args()

    net = SimpleNet(args.no_of_switches)
    net.start()

    first = net.hosts[0]
    last = net.hosts[1]

    count = args.count

    command = str.format('ping -c {} {}', count, last.IP())
    print first.cmd(command)
    net.stop()