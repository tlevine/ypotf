import smtplib
import logging

from . import searches

logger = logging.getLogger(__name__)

class LimitedSMTP(smtplib.SMTP_SSL):

    def __init__(self, N, *args, **kwargs):
        '''
        :param int n: Max messages to send this session
        '''
        self.N = N
        self.n = 0
        super(LimitedSMTP, self).__init__(*args, **kwargs)

    def sendmail(self, *args, **kwargs):
        self.n += 1

        if self.N == None:
            pass # No rate limit
        elif self.n < self.N:
            logger.info('%d of %d messages sent' % (self.n, self.N))
        else:
            raise RuntimeError('Rate limit exceeded')

        return super(LimitedSMTP, self).sendmail(*args, **kwargs)

def quota(M, quotas):
    '''
    :param iter quotas: A stream of quota strs in the form
        "$minutes:$count", the count of emails that you are allowed to
        send within that many minutes
    :returns: The number of emails you are allowed this session
    :rtype: int or NoneType
    '''
    N = None
    for quota in quotas:
        minutes, count = map(int, quota.split(':'))
        n = count - searches.n_sent(M, minutes)
        if N == None or n < N:
            N = n
    return N
