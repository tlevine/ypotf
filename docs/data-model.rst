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

1. Pending (Flagged UNANSWERED)
2. Pending unsubscriptions (Flagged ANSWERED UNSEEN)
3. Applied commands/data (Flagged ANSWERED SEEN)

Secondary and tertiary types are encoded in headers.

1. Pending (Flagged UNANSWERED)

  1. Incoming commands (X-Ypotf-Kind is absent)

    1. help (Subject is "help".)
    2. list-archive (Subject starts with "list-archive".)
    3. subscribe (Subject is "subscribe".)
    4. unsubscribe (Subject is "unsubscribe".)
    5. list-confirm (Subject contains a confirmation code.)
    6. message (All other subjects)

  2. Pending subscriptions (X-Ypotf-Kind is "Subscription".)
  3. Pending publications (X-Ypotf-Kind is "Publication".)

2. Pending unsubscriptions (Flagged ANSWERED UNSEEN)

3. Applied commands/data (Flagged ANSWERED SEEN)

  1. Applied commands (X-Ypotf-Kind is not set.)
  2. Current subscriptions (X-Ypotf-Kind is "Subscription".)
  3. Current publications (X-Ypotf-Kind is "Publication".)

Messages take one of the following paths through these states.


