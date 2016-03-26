import imaplib
import os

from . import processors

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    while True:
        M.select('INBOX')
        nums = processors.message_nums(M)
        if len(nums) > 0:
            processors.process(M, nums[0], m)
            M.close()
        else:
            M.close()
            break
    M.logout()

def cli():
    ypotf('mail.gandi.net', '_@dada.pink', os.environ['PASSWORD'])
#   import horetu
#   horetu.horetu(ypotf)
