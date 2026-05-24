## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - Reflected
- **Lab URL:** [Lab: Reflected XSS into HTML context with nothing encoded](https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded)
- **Date Solved:** 24/5/2026
## Vulnerability Summary

The search functionality reflects user input directly into the HTML response without any encoding or sanitization. Injecting a `<script>` tag into the search query causes the browser to execute it as JavaScript, making the server return the payload back to the victim's browser verbatim.
## Reconnaissance

- Entering a normal string like `test` into the search bar produces this request: `GET /?search=test`, and the string is reflected back in the response body inside a `<h1>` element: `<h1>1 search results for 'test'</h1>`. User input is being placed directly into the HTML without escaping.
- Testing `<` in the search field shows the character rendered literally in the page source, not as `&lt;`. No HTML encoding is applied to user input.
## Exploitation Steps

1. Navigate to the lab's search functionality.
2. Enter `<script>alert(1)</script>` in the search box and submit.
3. The server reflects the payload back into the page and the browser executes it, triggering an `alert(1)` dialog. The lab is solved.

We can also inject the payload directly via the URL:
`https://...web-security-academy.net/?search=<script>alert(1)</script>`
## Payload Used

`<script>alert(1)</script>`
The search term is reflected directly into the HTML body with no encoding, so any injected tag is treated as valid markup by the browser. The `<script>` tag tells the browser to execute its contents as JavaScript, causing `alert(1)` to run in the victim's origin.
## Root Cause

User-controlled input from the `search` parameter is concatenated into the HTML response without output encoding.
## Remediation

HTML-encode all user-supplied values before inserting them into the page. In most server-side frameworks this is the default behavior of the templating engine:
````python
from markupsafe import escape

search_term = escape(request.args.get("search", ""))
html = f"<h1>Search results for '{search_term}'</h1>"
````
`<` becomes `&lt;`, `>` becomes `&gt;`, so the injected tag is displayed as text rather than interpreted as markup.
