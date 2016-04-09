import sys
import subprocess, os

def subscribe(m):
    '''
    '''
    x = ['Approve', 'Read', 'Confiration email']
    while True:
        y = _question('Review request from "%(From)s"?' % m, x, 2)
        if y == 'Read':
            _pager(m.as_string())
        else:
            return y == 'Approve'

def _question(text, choices, default=0):
    if len(set(c[0] for c in choices)) != len(choices):
        raise ValueError('Choices conflict.')

    original_choices = list(choices)
    short_options = [c[0].lower() for c in original_choices]
    long_options = [c.lower() for c in original_choices]
    default_choices = list(long_options)
    default_choices[default] = default_choices[default].title()

    p = '/'.join('[%s]%s' % (c[0], c[1:]) for c in default_choices)
    while True:
        y = input('%s\n(%s): ' % (text, p)).lower()
        if y == '':
            i = default
        elif y in short_options:
            i = short_options.index(y)
        elif y in long_options:
            i = long_options.index(y)
        else:
            continue
        break


    return original_choices[i]



def _pager(text):
    sp = subprocess.Popen(os.environ["PAGER"],
        stdin=subprocess.PIPE, shell=True)
    sp.stdin.write(text.encode('utf-8'))
    sp.stdin.close()
    sp.wait()
