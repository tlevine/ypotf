import imaplib

* Confirmations
* Queued messages


def confirm(confirmation_code):
    '''
    Based on a confirmation code, determine what action to take next.

    :param str confirmation_code: Confirmation code from email
    :rtype: Action
    :returns: Action to take based on the confirmation code
    '''


class Folder(object):
    def __init__(self, name):
        self.name = name
        
        M.select('INBOX')

    def close(self):
        self.M.close()
        self.M.logout()

    def peek(self) -> Tuple[bytes,bytes]:
        'Look at an arbitrary email.'
        typ, data = self.M.search(None, 'ALL')
        nums = data[0].split()

        # Read the first one if it's available.
        if nums == []:
            return None, None
        else:
            num = nums[0]
            typ, data = self.M.fetch(num, '(RFC822)')

            # Email is ASCII http://en.wikipedia.org/wiki/MIME
            return num, data[0][1]
