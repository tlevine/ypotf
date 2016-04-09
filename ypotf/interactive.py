import sys
import subprocess, os

def subscribe(m):
    '''
    '''
    a = _question('Review request from %(From)s' % m)


def _question(text, choices, default=0):
    if len(set(c[0] for c in choices)) != len(choices):
        raise ValueError('Choices conflict.')

    original_choices = list(choices)
    short_options = set(c[0].lower() for c in original_choices)
    long_options = [c.lower() for c in original_choices]
    default_choices = [long_options[0].title()] + long_options[1:]

    p = '/'.join('[%s]%s' % (c[0], c[1:]) for c in default_choices)
    y = input('%s (%s)? ' % (text, p)).lower()
    if y in short_options:
        i = short_options.index(y)
    elif y in long_options:
        i = long_options.index(y)
    else:
        i = default

    return original_choices[i]



def _pager(text):
    sp = subprocess.Popen(os.environ["PAGER"],
        stdin=subprocess.PIPE, shell=True)
    sp.stdin.write(text.encode('utf-8'))
    sp.stdin.close()
    sp.wait()
