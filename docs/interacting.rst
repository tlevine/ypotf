Interacting with a mailing list
-------------------------------
To send an email to list members, you pretty much just send an email to
the mailing list email address. To otherwise interact with the mailing
list, like to subscribe to the list, you need to specify the type in the
subject line.

Here are the subject line formats associated with each sort of email.

.. csv-table ::
  
    Type of email,Subject line
    Subscription request,\"subscribe\" (case-insensitive)
    Unsubscription request,\"unsubscribe\" (case-insensitive)
    Response to confirmation email,a confirmation identifier
    View list archives,\"list-archive\"\, followed by a query
    Request for documentation,\"help\" (case-insensitive)
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
Messages to list members are the whole point of ypotf, of course.
In response to a message to list members, ypotf sends a confirmation
email. If the confirmation succeeds, the original email gets sent to
all members of the list with the following email headers.

From
    The address that sent the email
To
    The mailing list email address
Reply-To
    The mailing list email address

People can send messages to the list regardless of whether they are
subscribed as list members; subscription determines only whether people
receive emails.

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

The subject of the response email contains a confirmation identifier
of the following format

    list-confirm-$identifier

where "identifier" is a long string that should be hard to type by
accident.

View list archives
^^^^^^^^^^^^^^^^^^
This feature has not been implemented.

Request for documentation
^^^^^^^^^^^^^^^^^^^^^^^^^
When a documentation is requested, ypotf replies with a summary of the
commands that you can send, similar to the present documentation.

Message type flow
^^^^^^^^^^^^^^^^^
All requests to the list lead to something else happening; here's the
whole network of it all.

.. graphviz:: flow.dot

ypotf stores all of its mailing list information in email messages.
Requests arrive (right arrow nodes in the above diagram) as emails in
the "inbox" folder. They start out with the Recent flag, but ypotf
ignores that flag. Each message is flagged "Seen" after being fully
processed.

When emails need to be sent (left arrow nodes in the above diagram),
they are sent over SMTP and placed in the "Sent" folder.

Requests to subscribe, unsubscribe, or send a message, and confirmations
for these requests, require two sorts of temporary information to be
stored on the server in the following places.

Queued subscription
    Stored in the inbox with the Flagged and Draft flags both set
Queued messages
    Stored in the inbox with the Draft flag

In response to a request to subscribe or unsubscribe, ypotf creates a
queued subscription email. The "To" field is a randomly generated
confirmation code that also gets sent to the requestor, and the subject
is the email address of the requestor.

In response to a message request, ypotf creates a new message that is a
copy of the incoming message except with the Draft flag set and with the
following changes in the headers.

Bcc
    The confirmation code
Reply-To
    The mailing list address
Subject
    The mailing list prefix plus the original subject

Note that confirmation codes are in the "Bcc" field.
This is better than an X-* field because the server is more likely to
support searching on it and because it is easier to see in a MUA.

These three sorts of requests also result in the sending of a
confirmation email, with the aforementioned confirmation code in the
subject of the confirmation email. The email instructs the recipient to
reply to the email as confirmation that he or she controls the email
address.

Archive requests, help requests, and erroneous messages do not require
confirmation, so those requests are handled in one email response;
they don't require the aforementioned confirmation procedure.

Sending messages
^^^^^^^^^^^^^^^^^^^^
ypotf sends messages to one recipient at a time. It stores the following
records of sent messages.

1. A copy of every message that is sent
2. An additional copy for every message sent to the full subscription
   list ("message"-type messages rather than "help", "confirm", or
   "list-archive" messages)

It stores both of these in the "Sent" folder. We can tell them apart
because the first kind has a "Bcc" header and the second does not.

Copies of individual sends
~~~~~~~~~~~~~~~~~~~~~~~~~~
The first kind of message is an exact copy of the message that is passed
to the SMTP server. It includes the following ypotf-specific flags

X-Ypotf-Id
    A random number that we need because sent messages share message-ids.
X-Ypotf-Date
    The date at which Ypotf sent the message

This kind of message is stored only for record-keeping; aside from
saving them, ypotf ignores these messages.

I intend for this to record only the ones where sending actually
succeeded; here is how I do that.

1. I start out with the Inbox IMAP folder selected; everything in Ypotf
   except for the saving of sent messages happens in the Inbox folder.
2. Append the message to the Sent folder (IMAP).
3. Try sending the message with SMTP.
4. If sending fails: Select the Sent folder, find the message based on
   the "X-Ypotf-Id" header, delete it, and exit the program with an
   error message.

Thus, if we intended to send a message to all list subscribers but the
message was in fact sent only to a few of them, we can tell which ones
received it and which ones didn't. A neat feature would be to finish
sending partially sent batches of messages.

Additional message-type batch copy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The second kind of message in the Sent folder is a record of each batch
of messages that was sent. Ypotf references this kind of message in
response to list-archive queries.

It is saved before all messages of the first kind are saved, so it is a
record of what was supposed to happen rather than what really happened.
It has nothing to do with what was sent to the SMTP server.

That said, its format is easier explained as a modification of a message
of the first kind; you can create this sort of message by starting with
any message of the first kind and making the following changes.

* Add a "Bcc" header listing all of the present subscribers, that is,
  all of the people who were supposed to receive the message, regardless
  of whether the SMTP sending in fact succeeded.
* Generate a new "X-Ypotf-Id" header.
* Change the "X-Ypotf-Date" header; the second kind of message is sent
  before the first kind of message is.

Again, this message is *not* sent to the SMTP server.

The list-archive feature doesn't need to know what the list members
were, but I thought it would be nice to have them in here anyway.

* With the list of present subscribers, this kind of message becomes a
  concise version of the first type of message; the only thing that it
  lacks is the exact dates of sending.
* The list of present subscribers functions as a record of the
  historical subscriber list that is easy to view in a mail user agent.
* This list includes the full list of recipients that were intended in
  the batch, whereas the first kind of message includes only the ones
  for whom sending was successful.

Logs
^^^^^
ypotf retains all messages that it ever creates. This includes

* All messages that ever arrive in the inbox
* All versions of all messages that it creates in the inbox
* All messages that it ever sends, one copy per recipient
* All records of sent messages

When it is finished processing an incoming message, ypotf flags that
message as "Seen" and "Answered". When it is finished processing a
message that it created (a queued subscription or queued message), it
marks that message as "Answered". That is, ypotf uses "Answered" in all
places where "Deleted" would be a reasonable choice.

For large mailing lists, it may be helpful to add a flag for at least
batch deletes from the inbox directory; it would be safe to delete all
messages all "Answered" messages, as those are already ignored anyway.

    C: A003 SELECT INBOX
    C: A004 SEARCH ANSWERED

It could also be helpful, for large mailing lists, to delete copies of
the individual message sends (kind 1). Almost all of the information in
these messages is in the additional per-batch message (kind 2), and
I save the first kind of message only for debugging failed messages.
It would be safe to delete all messages in Sent that lack a Bcc.

    C: A003 SELECT Sent
    C: A004 SEARCH NOT BCC ""
