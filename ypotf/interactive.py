import subprocess, os
def subscribe(m):
    '''
    '''



def _pager(text):
    sp = subprocess.Popen([os.environ["EDITOR"]])
    sp.wait()
