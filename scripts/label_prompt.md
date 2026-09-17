# Labelling prompt (Person B)

Paste this into Claude, then attach or paste one batch file. Use the same prompt for every batch.
Fill in the label guidelines from MAPENS_CONTEXT.md section 6.2 before the first batch and do not change them later.

---

You are labelling informal Serbian Viber messages from traffic groups in Novi Sad.

For each input line ({"id", "text"}) output exactly one JSON line:
{"id": <same id>, "label": "<noise|patrol|accident|jam|clear>", "locations": [{"text": "<exact substring of text>", "start": <char offset>, "end": <char offset>}]}

Label guidelines:
TODO(B): copy the guidelines from MAPENS_CONTEXT.md section 6.2

Rules:
- Output only JSON lines, one per input message, in the same order, nothing else.
- "text" in locations must be copied exactly from the message, including case and missing diacritics.
- A location is any place reference: street, square, bridge, shop, fuel station, neighbourhood, landmark, nickname.
- If there is no location, use "locations": [].
