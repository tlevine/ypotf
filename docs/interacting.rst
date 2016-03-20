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
    Response to confirmation email,a valid confirmation identifier
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

If the email address is already on the list, ypotf replies with an error
message explaning that the address is already on the list.

Otherwise, ypotf sends a confirmation message. If the
**confirmation process** suceeds,
the email address is added to the **list members**.

Unsubscription requests
^^^^^^^^^^^^^^^^^^^^^^^
An unsubscription request is a request for one email address to stop
receiving messages that are sent to list members.

If the email address is not already on the list, ypotf replies with an
error message explaning that the address isn't subscribed and thus can't
be removed from the list.

Otherwise, ypotf sends a confirmation message. If the
**confirmation process** suceeds,
the email address is removed from the **list members**.

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

Response to confirmation email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Confirmation emails exist to protect against email spoofing attacks.

Every particular confirmation email corresponds to a particular
subscribe request, unsubscribe request, or message to list members.
The confirmation email directs the recipient to reply to the email,
as this composes an email with the appropriate subject.
After the confirmation is returned, the original request is processed.

View list archives
^^^^^^^^^^^^^^^^^^
This feature has not been implemented.

Request for documentation
^^^^^^^^^^^^^^^^^^^^^^^^^
When a documentation is requested, ypotf replies with a summary of the
commands that you can send, similar to the present documentation.

Message type flow
^^^^^^^^^^^^^^^^^

(Make a graphviz thing.)
