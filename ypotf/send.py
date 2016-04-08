import logging

from . import search

logger = logging.getLogger(__name__)

FORWARDED_HEADERS = {
    'from', 'to',
    'cc', 'subject', 'date',
    'user-agent',
    'mime-version', 'content-type', 'content-transfer-encoding',
    'message-id', 'in-reply-to', 'references',
}
LIST_HEADERS = {
    'From': '_@dada.pink',
    'List-Id': '_.dada.pink',
    'List-Unsubscribe': 'mailto:_@dada.pink?subject=unsubscribe',
    'List-Archive': 'mailto:_@dada.pink?subject=list-archive',
    'List-Post': 'mailto:_@dada.pink',
    'List-Help': 'mailto:_@dada.pink?subject=help',
    'List-Subscribe': 'mailto:_@dada.pink?subject=subscribe',
}

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
        for header in msg:
            if header.lower() not in FORWARDED_HEADERS:
                del(msg[header])
        if 'From' not in msg:
            for k, v in LIST_HEADERS.items():
                if k in msg:
                    del(msg[k])
                msg[k] = v
        if '@' not in msg.get('To', ''):
            del(msg['To'])
            msg['To'] = list_address

        logger.debug(_log_tpl % msg)

        S.send_message(msg, list_address, [to_address])
        _append('Sent', M, '\\SEEN', msg)
