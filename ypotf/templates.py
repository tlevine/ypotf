from email.messages import Message

from jinja2 import Template

fn = os.path.abspath(os.path.join(__file__, '..', 'template.txt'))
with open(fn) as fp:
    TEMPLATE = Template(fp.read())

def render(subject, references, **kwargs):
    m = Message()
    m['Subject'] = subject
    m['References'] = references
    m.set_payload(TEMPLATE.render(**kwargs))
    return m
