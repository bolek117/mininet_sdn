"""
A spam-classifying POX component
To set parameters run with 'pox.py spam_class -parameter=value'
"""
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet import tcp

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
# _gateway_mac = EthAddr('00-00-00-00-00-00')
inspection_dict = {}
states = {'none': 1, 'pending': 2, 'ok': 3, 'wrong': 4, 'not_for_inspection': 5}
_gateway_dpid = 0


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
    time.sleep(0.5)     # Fake execution time

    if len(msg) == 0:
        return True

    msg = msg.rstrip().lower()

    for line in _words:
        # log.info('Msg: {}, wordlist: {}'.format(msg, _words))
        if msg.find(line) != -1:
            return False

    return True


def _is_valid_for_inspection(msg):
    return type(msg) is str and len(msg) != 0


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
    if _is_valid_for_inspection(msg):
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


def _decide_by_inspection_result(event):
    """
    :param event:
    :return: True if it was possible to decide (drop or flood). False if decision cannot be taken at the moment of calling
    """
    buffer_id = event.ofp.buffer_id
    state = inspection_dict[buffer_id]

    if state is states['ok'] or state is states['not_for_inspection']:
        flood(event)
    elif state is states['wrong']:
        log.info('Spam found, dropping buffer {}...'.format(buffer_id))
        drop(event)
    else:
        return False

    return True


def _packet_handler_mode2(event):
    global inspection_dict

    packet = event.parsed
    buffer_id = event.ofp.buffer_id
    dpid = event.dpid

    def _get_state_name(buffer_id):
        for key, value in states.iteritems():
            if value == inspection_dict[buffer_id]:
                return key
        return None

    # Packet has started inspection
    if buffer_id in inspection_dict.keys():

        # If not for inspection, just pass-by and exit from function
        if inspection_dict[buffer_id] is states['not_for_inspection']:
            flood(event)
            return

        log.info('[{}] Packet {} found in inspection table'.format(dpid, buffer_id))

        # Packet is on gateway (edge switch)
        if dpid == _gateway_dpid:
            log.info('[{}] Edge switch'.format(dpid))
            while not _decide_by_inspection_result(event):
                wait_time = 1.0 / 100  # 0.01 second, 10 miliseconds

                log.info('[{}] Inspection not complete ({}), Waiting for {} seconds'
                         .format(dpid, _get_state_name(buffer_id), wait_time))
                time.sleep(wait_time)

            log.info('[{}] Inspection complete, result: {}'.format(dpid, _get_state_name(buffer_id)))
        else:
            if _decide_by_inspection_result(event):
                log.info('[{}] Passing by intermediate switch with status {}...'.format(event.dpid, _get_state_name(buffer_id)))
    else:
        log.info('[{}] Packet {} not found in inspection table'.format(dpid, buffer_id))

        inspection_dict[buffer_id] = states['none']
        flood(event)

        msg = _get_data_from_packet(packet)

        if _is_valid_for_inspection(msg):
            log.info('[{}] Is valid for inspection [{}]'.format(dpid, msg.rstrip()))

            # Mark as inspection pending and start inspection
            inspection_dict[buffer_id] = states['pending']
            log.info('[{}] Inspecting'.format(dpid))
            if _inspect(_get_data_from_packet(packet)):
                inspection_dict[buffer_id] = states['ok']
            else:
                inspection_dict[buffer_id] = states['wrong']
            log.info('[{}] Inspected, state {}'.format(dpid, _get_state_name(buffer_id)))
        else:
            log.info('[{}] Not valid for inspection'.format(dpid))
            inspection_dict[buffer_id] = states['not_for_inspection']
            # log.info('[{}] Setting state to "not_for_inspection".\nChecking actual state: ... {}'
            #          .format(dpid, _get_state_name(buffer_id)))

    log.info('-----')


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


def _register_last_switch(event):
    global _gateway_dpid

    switch_id = event.dpid

    if _gateway_dpid < switch_id:
        log.info('Changing gateway id to {}'.format(switch_id))
        _gateway_dpid = switch_id


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
    # _gateway_mac = EthAddr(gateway_mac)

    log.info('Mode is {}'.format(_mode))

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

    core.openflow.addListenerByName("ConnectionUp", _register_last_switch)

    if _mode == 1:
        core.openflow.addListenerByName("PacketIn", _packet_handler_mode1)
    elif _mode == 2:
        core.openflow.addListenerByName("PacketIn", _packet_handler_mode2)
    else:
        log.error('Invalid mode')
        sys.exit(-2)
