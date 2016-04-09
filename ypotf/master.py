import logging
from copy import deepcopy

from .utils import r

logger = logging.getLogger(__name__)

log_tpl = '''%s this message to %s
----------------------------------------
%s
----------------------------------------''' 

class Mail(object):
    def __init__(self, S, M, list_address):
        self._S = S
        self._M = M
        self._list_address

    def __enter__(self, box='Inbox'):
        self._finalize = []
        self._revert = []
        self._select(box)
        return self

    def _select(self, box):
        if self._box != box:
            self._box = box
            r(self._M.select(self._box))
            logger.debug('Selected box %s' % self._box)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            for f, args in self._finalize:
                f(*args)
        else:
            logger.info('Exception occurred in transaction, aborting.')
            for f, args in self._revert:
                f(*args)
        r(self._M.close())

    def store_applied(self, num):
        return self.store(num, '+FLAGS', '\\ANSWERED \\SEEN')

    def store_pending(self, num):
        return self.store(num, '-FLAGS', '\\ANSWERED')

    def store_deleted(self, num, flags):
        return self.store(num, '+FLAGS', '\\DELETED')

    def append_applied(self, m):
        return self._append('Inbox', '\\ANSWERED \\SEEN', m)

    def append_pending(self, m):
        return self._append('Inbox', '\\SEEN', m)

    def append_sent(self, m):
        return self._append('Sent', '\\SEEN', m)

    def _store(self, num, action, flags):
        actions = {
            '+FLAGS': '-FLAGS',
            '-FLAGS': '+FLAGS',
        }
        if action in actions:
            anti_action = actions[action]
            self._revert.append((self._store, (num, anti_action, flags)))
            return self._revert_store(num, action, flags)
        else:
            raise ValueError('Bad action: %s' % action)

    def _revert_store(self, *args):
        '''
        :param args: Tuple of num, action, flags
        '''
        logger.debug('STORE %d %s (%s)' % *args)
        return r(self._M.store(*args))

    def _append(self, box, flags, m):
        '''
        It is possible to append to boxes other than the current one.
        This gets interesting.
        '''
        if 'seen' not in flags.lower():
            raise ValueError('"\\Seen" must be a flag.')
        logger.debug(log_tpl % ('Appending', to_address, msg1))

        append_id = _uuid()
        m['X-Ypotf-Append'] = append_id

        # Reverting an append may require a switch of box.
        # Put it at the beginning of the revert list so it runs last.
        self._revert.insert(0, self._revert_append, (box, append_id))

        d = tuple(_now().timetuple())
        return r(self._M.append(box, flags, d, m.as_bytes()))

    def _revert_append(box, append_id):
        query = 'HEADER X-Ypotf-Append %s' % append_id))
        self._select(box)
        
        num = search.get_num(M, query)
        self._store(num, '+FLAGS', '\\DELETED')

    def send(self, msg, *to_addresses):
        logger.info('Sending to %d addresses' % len(to_addresses))
        msg2 = _prepare_send(msg) # sent message kind 2

        if msg2['To'].lower() == self._list_address:
            msg2['Bcc'] = ', '.join(to_addresses)
            self._append('Sent', '\\SEEN', msg2)

        for to_address in to_addresses:
            msg1 = _prepare_send(msg) # sent message kind 1
            logger.debug(log_tpl % ('Sending', to_address, msg1))
            self._append('Sent', '\\SEEN', msg1)
            self.S.send_message(msg1, self._list_address, [to_address])
