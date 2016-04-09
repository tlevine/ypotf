import subprocess, os

def subscribe(m):
    '''
    '''



def _pager(text):
    sp = subprocess.Popen(os.environ["PAGER"],
        stdin=subprocess.PIPE, shell=True)
    sp.stdin.write(text.encode('utf-8'))
    sp.stdin.close()
    sp.wait()
