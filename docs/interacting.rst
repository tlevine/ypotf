Interacting with a mailing list
-------------------------------
To send an email to list members, you pretty much just send an email to
the mailing list email address. To otherwise interact with the mailing
list, like to subscribe to the list, you need to specify the type in the
subject line.

Here are the subject line formats associated with each sort of email.

.. csv-table ::
  
    Type of email,Subject line
    Subscription request,"subscribe" (case-insensitive)
    Unsubscription request,"unsubscribe" (case-insensitive)
    Response to confirmation email,"list-confirm"\, followed by an identifier
    View list archives,"list-archive"\, followed by a query
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
messages that are sent to list members.

If ypotf was run with the ``--private`` flag, the


In either case, ypotf sends a confirmation message. If the
**confirmation process** suceeds,
the email address is added to **list members**.

Messages to the list members
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note that ypotf does not allow you to send messages with the following
subject lines, case-insensitive.

* "unsubscribe"
* "subscribe"
* "help"

These subjects are vague anyway, so I don't care to support them;
if you want to send a message with any of the above subject lines,
change the subject, or just add a meaningless word like "please".

Message type flow
^^^^^^^^^^^^^^^^^

(Make a graphviz thing.)
