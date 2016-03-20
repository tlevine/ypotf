Interacting with a mailing list
-------------------------------
People can send the following sorts of emails to the email account.

* Subscription requests
* Unsubscription requests
* Responses to confirmation emails
* Requests for documentation on using the mailing list
* Messages to the list's members

The type of email is specified in the subject line of the email;
here are the subject line formats associated with each sort of email.

.. csv-table ::
  
    Type of email,Subject line
    Subscription request,"subscribe" (case-insensitive)
    Unsubscription request,"unsubscribe" (case-insensitive)
    Response to confirmation email,"ytotf-confirm"\, followed by an identifier
    Request for documentation,"help" (case-insensitive)
    Messages to the list members,Anything else

Some of these make sense only if you have a certain status; for example,
subscription requests make sense only if you are subscribed. If you try
to send something that doesn't make sense, it is mostly treated as a
documentation request.

Now let's discuss what each of these sorts of emails do.

Subscription requests
^^^^^^^^^^^^^^^^^^^^^
A subscription request is a request for one email address to receive
messages that are sent to list members. In response to such a request,
ypotf sends a confirmation message

Messages to the list members
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note that ypotf does not allow you to send messages with the following
subject lines, case-insensitive.

* "unsubscribe"
* "subscribe"
* "ypotf-confirm", followed by anything
* "help"

These subjects are vague anyway, so I don't care to support them;
if you want to send a message with any of the above subject lines,
change the subject, or just add a meaningless word like "please".

Message type flow
^^^^^^^^^^^^^^^^^

(Make a graphviz thing.)
