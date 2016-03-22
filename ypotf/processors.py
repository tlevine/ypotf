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
    M.select('confirmations')

def subscribe(M, email_address):
    M.select('ypotf-list')

def unsubscribe(M, email_address):
    M.select('ypotf-list')

def send_message(M, message_id):
    M.select('ypotf-queue')

def queue_message(M, message_id):
    M.select('ypotf-queue')


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
