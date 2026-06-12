## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - Reflected
- **Lab URL:** [Lab: Reflected XSS into a JavaScript string with angle brackets HTML encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-html-encoded)
- **Date Solved:** 12/6/2026
## Vulnerability Summary

The app contains a reflected XSS vulnerability in the search functionality. The user-supplied input is inside a quoted string literal. It does attempt to perform HTML encoding with angle brackets, but does not do so with apostrophes (`'`). Thus, we can still exploit XSS by breaking out of this existing string and injecting our own `JavaScript` statement.
## Reconnaissance

-  Entering a normal string like `aaa` into the search bar produces this request: `GET /?search=aaa`, and the string is reflected back in the response body inside the `JavaScript` `<script>` tags as follows:
```html
<script>
    var searchTerms = 'aaa';
    document.write('<img src="/resources/images/tracker.gif?searchTerms=' + encodeURIComponent(searchTerms) + '">');
</script>
```
- Trying to break out of the existing `JavaScript` block with the `</script>` tag and inject our own payload with `</script><script>alert(1)</script>`, we get a response that reads:
```html
<script>
    var searchTerms = '&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;';
                        document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
</script>
```
Angle brackets are HTML-encoded as `&lt;` and `&gt;`, so our payload cannot contain them.
## Exploitation Steps

1. Type in a random string into the search bar, e.g. `aaa`. Intercept this request.
2. Paste the payload below onto the `search` parameter and send request:
```
';alert(1)//
```
3.  You should get a `200 OK` HTTP Response. Copy the response URL and open it in browser. The `alert()` function should trigger and lab is solved.
## Payload Used

`';alert(1)//`
- The `'` breaks us out of the existing string literal.
- The statement terminator (`;`) ends the existing `var searchTerms = ''` statement. This helps us to introduce `alert(1)` to be executed as a standalone `JavaScript` statement.
- The `//` comments out the rest of the query, preventing an `Unterminated string literal` error.
## Root Cause

The app fails to properly escape user-supplied input when reflecting it directly into a JavaScript string context. By failing to use backslash escaping (e.g., `\'`) or Unicode escapes for single quotes, an attacker can break out of the string literal and append malicious JavaScript statements.
## Remediation

The app must implement context-aware output encoding.
- **HTML Encoding:** Because the JavaScript is embedded within an HTML document, characters with special meaning in HTML (such as `<`, `>`, `&`, `"`, and `'`) must be converted to their corresponding HTML entities (e.g., `<` becomes `&lt;`).
- **JavaScript Unicode Escaping:** When reflecting untrusted data into a JavaScript string, use Unicode escapes for safety. For example, `<` should be encoded as `\u003c`. Modern web frameworks typically handle this automatically if data is passed to the DOM safely (e.g., via `textContent`), but server-side rendering requires strict encoding before the response is constructed.