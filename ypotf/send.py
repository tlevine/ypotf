import logging

from . import search

logger = logging.getLogger(__name__)

log_tpl = '''Sending this message
----------------------------------------
%s
----------------------------------------'''
list_address = '_@dada.pink'

def send(S, M, msg, to_address):
    if to_address == None:
        to_addresses = search.inbox.subscribers(M)
        logger.info('Sending to %d addresses' % len(to_addresses))
    else:
        to_addresses = {to_address}
    for to_address in to_addresses:
        msg = templates....
        logger.debug(_log_tpl % msg)

        S.send_message(msg, list_address, [to_address])
        _append('Sent', M, '\\SEEN', msg)
