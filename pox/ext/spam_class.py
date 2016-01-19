"""
A spam-classifying POX component
To set parameters run with 'pox.py spam_class -parameter=value'
"""
from pox.lib.addresses import IPAddr, EthAddr

__author__ = 'mwitas'

import sys
import os
import time
import pox.openflow.libopenflow_01 as of  # OpenFlow 1.0 library
import pox.lib.util as poxutil  # Various util functions
from pox.core import core  # Main POX object
from pox.lib.revent import EventRemove

_workdir = os.environ['HOME'] + '/pox/ext/'
_mode = 0
_words = []
log = core.getLogger()  # Create a logger for this component

# Mode 1 specific fields
inspection_buffer = []

# Mode 2 specific fields
_gateway_mac = EthAddr('00-00-00-00-00-00')
inspection_dict = {}
states = {'none': 1, 'pending': 2, 'ok': 3, 'wrong': 4}

log = core.getLogger()  # Create a logger for this component


def _get_data_from_packet(parsed_packet, packet_type='ipv4'):
    # Consider only packets of type of 'packet_type'
    if parsed_packet.find(packet_type):

        # Strip first layer of encapsulation
        data = parsed_packet.payload

        # Strip next layers if possible to go to source packet
        while data.find(packet_type):
            data = data.payload

        # Return payload of source packet
        return data.payload


def _set_miss_length(event=None):
    if not core.hasComponent('openflow'):
        return
    core.openflow.miss_send_len = 0x7fff
    core.getLogger().info("Setting switches to forward full packet payloads")
    return EventRemove


def _inspect(msg):
    if len(msg) == 0:
        return True

    msg = msg.rstrip().lower()

    for line in _words:
        # log.info('Msg: {}, wordlist: {}'.format(msg, _words))
        if msg.find(line) != -1:
            return False

    return True


def _packet_handler_mode1(event):
    global inspection_buffer

    buffer_id = event.ofp.buffer_id

    # If not inspected before - note that inspection is pending, else pass-by
    if buffer_id not in inspection_buffer:
        inspection_buffer.append(buffer_id)
    else:
        flood(event)
        return

    msg = _get_data_from_packet(event.parsed)

    # Inspect only non-binary content and not empty packets
    if type(msg) is str and len(msg) != 0:
        log.info('Inspection of {} started, content [{}]'.format(buffer_id, msg.rstrip()))
        is_ok = _inspect(msg)

        if is_ok:
            flood(event)
        else:
            drop(event)
            log.error('{} SPAM packet found, dropping packet'.format(time.time()))

        log.info('-----')
        return
    else:
        flood(event)

    # Clean buffer if it is to much elements - leave last 64 elements
    if len(inspection_buffer) > 256:
        inspection_buffer = inspection_buffer[:-64]


def _packet_handler_mode2(event):
    # TODO
    pass


def flood(event):
    connection = event.connection
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.in_port = event.port
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    connection.send(msg)


def drop(event):
    return EventRemove


def _load_wordslist(path):
    global _words

    if not os.path.isfile(path):
        path = _workdir + path

    if not os.path.isfile(path):
        _words = []
        raise Exception('Badwords file not found ({})'.format(path))

    with open(path) as f:
        _words = [e.rstrip().lower() for e in f.readlines()]


@poxutil.eval_args
def launch(mode=1, wordslist='badwords.txt', gateway_mac='00-00-00-00-00-00'):
    """
    The default launcher that intercepts PacketIn events
    Modes:
        1 - hold on controller util classification ends
        2 - inspect on controller but allow forwarding to edge switch
    """
    global _mode
    _mode = mode

    _gateway_mac = EthAddr(gateway_mac)

    try:
        _load_wordslist(wordslist)
    except Exception as e:
        log.error(e.message)
        log.error('All packets will be marked as "valid"')

        while True:
            opt = raw_input("Do you want to continue (y/n)? ")
            if opt == 'y':
                break
            elif opt == 'n':
                log.error('Operation terminated')
                sys.exit(-1)

    if _set_miss_length() is None:
        core.addListenerByName("ComponentRegistered", _set_miss_length)

    if _mode == 1:
        core.openflow.addListenerByName("PacketIn", _packet_handler_mode1)
    elif _mode == 2:
        core.openflow.addListenerByName("PacketIn", _packet_handler_mode2)
    else:
        log.error('Invalid mode')
        sys.exit(-2)