import logging
from copy import deepcopy
import datetime

from .utils import r, uuid, search
from . import templates

logger = logging.getLogger(__name__)

log_tpl = '''%s this message to %s
----------------------------------------
%s
----------------------------------------''' 

class Writer(object):
    def __init__(self, list_address, S, M):
        self._S = S
        self._M = M
        self._list_address = list_address

    def __enter__(self, box='Inbox'):
        self._finalize = []
        self._revert = []
        self._box = box
        self._switched_box = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error('Exception occurred in transaction, aborting.')
            for f, args in self._revert:
                f(*args)

        if self._switched_box:
            r(M.logout(), 'BYE')
            sys.exit(1)

    def store_current(self, num):
        logger.debug('Storing message %s as current' % num.decode('ascii'))
        return self._store(num, '+FLAGS', '\\ANSWERED')

    def store_pending(self, num):
        logger.debug('Storing message %s as pending' % num.decode('ascii'))
        return self._store(num, '-FLAGS', '\\ANSWERED')

    def store_deleted(self, num, flags):
        logger.debug('Deleting message %s' % num.decode('ascii'))
        return self._store(num, '+FLAGS', '\\DELETED')

    def append_current(self, m):
        logger.debug('Appending new current message %(message-id)s' % m)
        return self._append('Inbox', '\\ANSWERED \\SEEN', m)

    def append_pending(self, m):
        logger.debug('Appending new pending message %(message-id)s' % m)
        return self._append('Inbox', '\\SEEN', m)

    def append_sent(self, m):
        logger.debug('Appending new sent message %(message-id)s' % m)
        return self._append('Sent', '\\SEEN', m)

    def _store(self, num, action, flags):
        actions = {
            '+FLAGS': '-FLAGS',
            '-FLAGS': '+FLAGS',
        }
        if action in actions:
            anti_action = actions[action]
            y = self._base_store(num, action, flags)
            self._revert.append((self._base_store, (num, anti_action, flags)))
            return y
        else:
            raise ValueError('Bad action: %s' % action)

    def _base_store(self, num, action, flags):
        '''
        :param args: Tuple of num, action, flags
        '''
        args = num.decode('ascii'), action, flags
        logger.debug('STORE %s %s (%s)' % args)
        return r(self._M.store(num, action, flags))

    def _append(self, box, flags, m):
        '''
        It is possible to append to boxes other than the current one.
        This gets interesting.
        '''
        if 'seen' not in flags.lower():
            raise ValueError('"\\Seen" must be a flag.')
        logger.debug(log_tpl % ('Appending', m['To'], m))

        m['X-Ypotf-Append'] = uuid()

        d = tuple(datetime.datetime.now().timetuple())
        l = m.as_bytes()
        y = r(self._M.append(box, flags, d, l))

        # Reverting an append may require a switch of box.
        # Put it at the beginning of the revert list so it runs last.
        self._revert.insert(0,
            (self._revert_append, (box, m['X-Ypotf-Append'])))

        return y

    def _revert_append(self, box, append_id):
        query = 'HEADER X-Ypotf-Append %s' % append_id

        if self._box != box:
            r(self._M.close())
            r(self._M.select(box))

        logger.debug('Selected box %s' % box)

        num = search(self._M, query)[0]
        self._store(num, '+FLAGS', '\\DELETED')

        if self._box != box:
            self._switched_box = True
            self._box = box

    def send(self, msg, to_addresses=None):
        publication = to_addresses != None

        if publication:
            msg2 = set_publication_batch_headers(deepcopy(msg), to_addresses)
            self._append('Sent', '\\SEEN', msg2)
        else:
            to_addresses = [msg['To']]

        logger.info('Sending to %d addresses' % len(to_addresses))
        for to_address in to_addresses:
            if publication:
                msg1 = templates.set_publication_headers(msg)
            else:
                msg1 = msg
            logger.debug(log_tpl % ('Sending', to_address, msg1))
            self._append('Sent', '\\SEEN', msg1)
            self._S.send_message(msg1, self._list_address, [to_address])
