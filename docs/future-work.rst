User interfaces

* Store ypotf X-headers, and use them to restore flags mailbox in case a
  human edits them by accident by opening the mailbox in a MUA.
* Come up with convenient ways of running it periodically.

Performance

* Before assembling lists of subscribers and confirmations and stuff,
  do a fast check to determine whether we need these lists.

Spam

* Sender blacklist
* Spam detection and command-line spam review
* Check whether the email came from the right server based on the
  DNS-based email certifications that I don't understand. Then only
  send confirmation emails for people who are not subscribed or whose
  SPF headers look odd.
  * http://www.openspf.org/SPF_Received_Header
  * https://pypi.python.org/pypi/pyspf/
  * http://www.openspf.org/FAQ/Envelope_from_scope
