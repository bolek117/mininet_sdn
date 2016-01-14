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

# Create a logger for this component
log = core.getLogger()
status = dict()


def _packet_handler(event):
    parsed = event.parsed
    desired = 'tcp'
    ip = parsed.find(desired)

    if ip is None:
        pck_type = pkt.ETHERNET.ethernet.getNameForType(parsed.type)
        log.info('- Packet is {}'.format(pck_type))
        flood(event)
    else:
        log.info('+ Packet is {}'.format(desired))
        log.info(event.data)
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
    core.openflow.addListenerByName("PacketIn", _packet_handler)
