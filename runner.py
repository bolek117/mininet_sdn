#!/usr/bin/env python
import sys

from topo.simpletopo import SimpleNet
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-s', '--switches', type=int, default=1, dest='no_of_switches',
                        help='Sets number of the switches in chain HOST_1 <-> Switch_1 <-> ... <-> Switch_N <-> HOST_2')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    net = SimpleNet(args.no_of_switches)
    net.start()

    first = net.hosts[0]
    last = net.hosts[1]

    while True:
        cmd = raw_input("$ ")

        if cmd == "exit" or cmd == "quit":
            net.stop()
            sys.exit(0)
        elif cmd == "monitor":
            lst = net.monitor()

            for i in lst:
                print i
                
        elif cmd == "pingall":
            print net.pingAll()
        else:
            print first.cmd(cmd)

