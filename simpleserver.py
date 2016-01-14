#!/usr/bin/env python
__source__ = 'http://ilab.cs.byu.edu/python/socket/echoserver.html'

"""
A simple echo server
"""

import socket
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=int, default=8080, help='Listening port')
    return parser.parse_args()


def do_server(port, size=1024):
    host = ''
    backlog = 5
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(backlog)

    while True:
        client, address = s.accept()

        data = client.recv(size)
        if data.lower().strip() != 'exit':
            data = 'Response: ' + data
            should_end = False
        else:
            data = 'Closing connection\n'
            should_end = True

        client.send(data)
        client.close()

        if should_end:
            s.shutdown(0)
            s.close()
            return

if __name__ == '__main__':
    args = parse_args()
    do_server(args.p)