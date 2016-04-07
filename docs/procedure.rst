ypotf runs three imap search commands. It is helpful to think about it
this way because a search command must be run on one folder and because
message indexes change with each search command.

1. Search the Sent folder with the SENTSINCE search key to assess quotas
   (one search per quota)
2. Search the Inbox folder for the subject fields of messages with the
   Flagged flag and without the Draft flag; these are the current
   subscribers.
3. Search for Draft (confirmation) and non-Seen (just-received) emails.
   * Assemble a mapping of confirmation code to message number
   * With each non-Seen email, process the email as a new command.

Quota
------
Count how many emails have been sent 
