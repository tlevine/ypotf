Ypotf stores its data in IMAP as a log that can be replayed.
It records changes in state only by appending new messages or
manipulating IMAP flags.

Sent folder
-------------
Messages in the Sent folders have these types

1. Exact copies of all messages that are sent out.
2. Aggregate of each batch of messages that is sent to the full
   subscriber list (not help requests, for example)

Messages in the Sent folder are never modified, and flags have no
meaning in this folder.

Inbox folder
-------------
Messages in the Inbox folders have three primary types, which are
encoded as flags.

1. Incoming commands (UNSEEN UNANSWERED UNDRAFT UNFLAGGED)
2. Processed commands (SEEN ANSWERED DRAFT UNFLAGGED)
3. Pending master data (SEEN ANSWERED UNDRAFT FLAGGED)
4. Current master data (SEEN ANSWERED UNDRAFT UNFLAGGED)


these types, which are organized as
primary and secondary types. Primary types are encoded in flags, and
secondary types are encoded in headers.

1. Incoming commands

  a. help
  b. list-archive
  c. subscribe
  d. unsubscribe
  e. list-confirm
  f. message

2. Pending master data

  a. Subscription requests
  b. Publication requests

3. Current master data

  a. Subscription requests
  b. Publication requests




    New command
        UNSEEN UNANSWERED UNDRAFT UNFLAGGED
    Pending subscription/message
        SEEN   UNANSWERED DRAFT   FLAGGED
    Manually cancelled pending subscription/message
        SEEN   UNANSWERED DRAFT   UNFLAGGED
    Current subscription/message
        SEEN   ANSWERED   UNDRAFT FLAGGED
    Manually cancelled current subscription/message
        SEEN   ANSWERED   UNDRAFT UNFLAGGED
    Commands that have completed
        SEEN   ANSWERED   DRAFT   UNFLAGGED
    Unused (I might use it for a blacklist.)
        SEEN   ANSWERED   DRAFT   FLAGGED
    Possible mistakes (ypotf will prompt for corrections.)
        SEEN UNANSWERED   UNDRAFT UNFLAGGED might occur because someone
        accidentally read a new command in a MUA;
        SEEN UNANSWERED   UNDRAFT FLAGGED might occurr because someone
        accidentally read a new command in a MUA and then flagged it;
        UNSEEN UNANSWERED UNDRAFT FLAGGED might occur because someone
        accidentally flagged a new command in a MUA.
        All other combinations with UNSEEN might occur because someone
        accidentally marked a message as unread in an MUA.
        
