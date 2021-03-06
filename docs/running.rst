Running a mailing list
----------------------
Install from PyPI. ::

    pip install ypotf

Make an email account, and run ypotf with the appropriate credentials.
The first time you run it, it's a good idea to run a test to make sure
that the credentials are set up properly. ::

    ypotf --username=ypotf@thomaslevine.com --password=acbeusar \
      --imap-host=mail.messagingengine.com:992 \
      --smtp-host=mail.messagingengine.com:465 \
      --test

Then run it without the test option. ::

    ypotf --username=ypotf@thomaslevine.com --password=acbeusar \
      --imap-host=mail.messagingengine.com:992 \
      --smtp-host=mail.messagingengine.com:465

ypotf processes any new emails that have been sent to the email address
(These are documented in the next section.) and then exits.
If you run ypotf this way, you have to run it periodically in order to
process any new commands; if you want it to run at 30-second intervals,
for example, you can run this.

    ypotf --username=ypotf@thomaslevine.com --password=acbeusar \
      --imap-host=mail.messagingengine.com:992 \
      --smtp-host=mail.messagingengine.com:465 \
      --watch=30s
