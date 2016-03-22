import re
from collections import namedtuple

NEWLINE = re.compile(r'[\r\n]+')
TYPES = {'subscribe', 'unsubscribe', 'message', 'error'}

Action = namedtuple('Action', ['type', 'argument'])

def factory(type_, argument):
    if type_ in TYPES:
        pass
    else:
        raise ValueError('Bad type: %s' % type_)

def loads(x):
    lines = list(filter(None, re.split(NEWLINE, x.strip())))
    if len(lines) >= 2:
        return Action(lines[0], '\n'.join(lines[1:]) + '\n')
    else:
        raise ValueError('Not a valid Action serialization')

def dumps(action):
    return '%s\n%s\n' % (action.type, action.argument)
