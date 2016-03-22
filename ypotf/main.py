def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
