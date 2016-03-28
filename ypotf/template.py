import os
from email.message import Message
from smtplib import SMTP

from jinja2 import Template

fn = os.path.abspath(os.path.join(__file__, '..', 'template.txt'))
with open(fn) as fp:
    TEMPLATE = Template(fp.read())

def configure(recipient, subject, references, to_address,
              **kwargs):
    m = Message()
    m['Subject'] = subject
    m['References'] = references
    if recipient == 'list':
        m['From'] = to_address
    elif recipient == 'sender':
        m['To'] = to_address
    else:
        raise ValueError('Bad recipient')
    m.set_payload(TEMPLATE.render(**kwargs))
    return m

def send(host, mailing_list_address, subscribers, m):
    if 'From' in m and 'To' not in m:
        m['To'] = mailing_list_address
        to_addrs = subscribers
    elif 'To' in m and 'From' not in m:
        m['Reply-To'] = m['From'] = mailing_list_address
        to_addrs = [m['To']]
    else:
        msg = 'Exactly one of "From" or "To" header should be set.'
        raise ValueError(msg)
    print(1)
    with SMTP(host) as smtp:
        print(2)
        smtp.send_message(msg=m, from_addr=mailing_list_address,
                          to_addrs=to_addrs)
    print(3)
