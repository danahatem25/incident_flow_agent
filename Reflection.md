# Reflection

## What was the hardest part?

The hardest part was dealing with the Gemini API changing under me while I was building. The library I started with turned out to be discontinued, so I had to switch to a newer one partway through. Then the specific AI model I picked kept becoming unavailable or hitting its daily usage limit — I'd get it working, then a few tests later it would stop responding, and I'd have to figure out whether it was a temporary server issue or a hard limit for the day. It took some trial and error to land on a model that was both available and had enough free daily usage to actually test with.

A smaller but tricky issue came up with ServiceNow itself. I expected an empty "description" field to simply be left blank, but ServiceNow was sending it as an explicit "no value" instead — and my code didn't expect that, so it rejected every ticket with an empty description. It was a good reminder that real systems don't always send data the way you'd assume, and testing with real tickets (not just the sample data) is what caught it.

## What would I improve with more time?

I'd make the "don't process the same ticket twice" safeguard permanent instead of temporary — right now it resets if the service restarts, which is fine for this project but wouldn't be ideal for real use. I'd also add a few more examples to my AI prompt to make its decisions even more reliable, since early on it sometimes matched tickets to the wrong solution just because they shared a general topic (like "email") rather than the actual problem. Finally, I'd add the same kind of retry safety net to the ServiceNow update step that I already added for the AI call, so that a brief outage on that end doesn't quietly leave a ticket unresolved.
