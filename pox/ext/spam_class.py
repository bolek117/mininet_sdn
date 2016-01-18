"""
A spam-classifying POX component
"""

__author__ = 'mwitas'

# Import some POX stuff
from pox.core import core  # Main POX object
import pox.openflow.libopenflow_01 as of  # OpenFlow 1.0 library

import pox.lib.packet as pkt  # Packet parsing/construction
from pox.lib.addresses import EthAddr, IPAddr  # Address types
import pox.lib.util as poxutil  # Various util functions
import pox.lib.revent as revent  # Event library
import pox.lib.recoco as recoco  # Multitasking library

from pox.lib.util import dpidToStr
from pox.lib.revent import EventRemove

# Create a logger for this component
log = core.getLogger()
status = dict()


def _get_data_from_packet(parsed_packet, packet_type='ipv4'):
    # Consider only packets of type of 'packet_type'
    if parsed_packet.find(packet_type):

        # Strip first layer of encapsulation
        data = parsed_packet.payload

        # If unpacked packet have some 'packet_type' packet inside
        # extract it
        while data.find(packet_type):
            data = data.payload

        # Return payload of lowest-lying packet
        return data.payload


def _packet_handler(event):
    parsed = event.parsed
    msg = _get_data_from_packet(parsed)

    if len(msg) > 0:
        log.info(msg)

    flood(event)


def flood(event):
    connection = event.connection
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.in_port = event.port
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    connection.send(msg)


@poxutil.eval_args
def launch():
    """
    The default launcher that intercepts PacketIn events
    """
    def set_miss_length (event = None):
        if not core.hasComponent('openflow'):
            return
        core.openflow.miss_send_len = 0x7fff
        core.getLogger().info("Requesting full packet payloads")
        return EventRemove

    if set_miss_length() is None:
        core.addListenerByName("ComponentRegistered", set_miss_length)

    core.openflow.addListenerByName("PacketIn", _packet_handler)
