Ypotf stores its data in IMAP as a log that can be replayed.
It records changes in state only by appending new messages or
manipulating IMAP flags.

Ypotf stores messages in the Inbox and Sent folders and never modifies
the messages themselves

Sent folder
-------------
Messages in the Sent folders have two types

1. Exact copies of all messages that are sent out.
2. Aggregate of each batch of messages that is sent to the full
   subscriber list (not help requests, for example)

Messages in the Sent folder are never modified

-------------



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
        
