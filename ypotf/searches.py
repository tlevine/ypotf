# Search the Sent folder with the SENTSINCE search key to assess quotas
# (one search per quota)
quota = {
    'folder': 'Sent',
    'criterion': 'SENTSINCE "01-JAN-2014"',
}    

# Search the Inbox folder for the subject fields of messages with the
# Flagged flag and without the Draft flag; these are the current
# subscribers.
subscribers = {
    'folder': 'Inbox',
    'criterion': 'FLAGGED UNDRAFT',
}

# Search for Draft (confirmation) and non-Seen (just-received) emails.
orders = {
    'folder': 'Inbox',
    'criterion': 'OR DRAFT UNSEEN',
}
