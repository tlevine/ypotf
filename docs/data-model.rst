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
Messages in the Inbox folders have two primary types, which are
encoded as flags.

1. Pending commands/data (UNANSWERED)
2. Applied commands/data (ANSWERED)

Secondary and tertiary types are encoded in headers; in the outline
below, the headers in parantheses distinguish among the sub-types.

1. Pending commands/data (X-Ypotf-Subscription)

  1. Incoming commands (Subject)

    1. help
    2. list-archive
    3. subscribe
    4. unsubscribe
    5. list-confirm
    6. message

  2. Pending subscriptions 

2. Applied commands/data (X-Ypotf-Subscription)

  1. Applied commands
  2. Current subscriptions
