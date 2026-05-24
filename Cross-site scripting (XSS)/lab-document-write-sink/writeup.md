## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - DOM-based
- **Lab URL:** [Lab: DOM XSS in document.write sink using source location.search](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink)
- **Date Solved:** 24/5/2026
## Vulnerability Summary

The search functionality uses client-side JavaScript to read the search query from `location.search` and pass it unsanitized into `document.write`, which writes raw HTML directly into the DOM. Injecting HTML-breaking characters into the search query allows an attacker to escape an `<img>` attribute context and inject arbitrary tags, triggering JavaScript execution entirely on the client side with no server-side reflection involved.
## Reconnaissance

- Entering a random string like `abc123` into the search box and inspecting the page source shows the string placed inside an `<img>` tag attribute: `<img src="/resources/images/tracker.gif?searchTerms=abc123">`. A JavaScript snippet on the page reads `location.search` and passes the value directly to `document.write` to construct this tag.
- Since `document.write` writes raw HTML, any characters we inject (including `"`, `>`, `<`) will be interpreted as markup by the browser's HTML parser rather than escaped as text.
## Exploitation Steps

1. Navigate to the lab and enter any search query to confirm the `<img>` tag structure in the page source (right-click → Inspect).
2. Enter the payload `"><svg onload=alert(1)>` in the search box.
3. The JavaScript constructs `<img src="/...?searchTerms="><svg onload=alert(1)>">`. The `"` closes the `src` attribute, `>` closes the `<img>` tag, and the `<svg onload=alert(1)>` tag is then written as a new element into the DOM. The browser fires `onload` and executes `alert(1)`. The lab is solved.
## Payload Used

`"><svg onload=alert(1)>`
The payload works by exploiting the context that user input lands in: the value of a `src` attribute within an `<img>` tag. The `"` terminates the attribute value, `>` terminates the tag, and the following `<svg onload=alert(1)>` is then a free-standing HTML element whose `onload` event fires immediately when it is written into the DOM via `document.write`.
## Root Cause

The page contains a JavaScript sink (`document.write`) that receives data from a taint source (`location.search`) without any sanitization or encoding. Because this happens entirely in the browser, standard server-side output encoding offers no protection — the vulnerability exists purely in the client-side code.
## Remediation

-  Replace `document.write` with safe DOM APIs that do not parse HTML. Use `textContent` or `createElement` + `setAttribute` instead:
```javascript
const img = document.createElement("img");
img.setAttribute("src", `/resources/images/tracker.gif?searchTerms=${encodeURIComponent(searchTerms)}`);
document.body.appendChild(img);
```
- Apply a strict Content Security Policy to block inline event handlers (`script-src 'self'`).
