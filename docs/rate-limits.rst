Many email providers have
`rate limits <https://www.fastmail.com/help/account/limits.html>_`.
ypotf can postpone sending of emails based on specified rate limits.

::

    ypotf --limit 10:2000 --limit 60:4000 --limit 1440:8000

ypotf counts how many emails were sent within each of the specified
durations, based on their presence in the "sent" folder.
If processing a particular request would pass the limit, ypotf exits
without processing the request; the next time that ypotf is run,
it will make the same check, but with the new date range.
