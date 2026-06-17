## Metadata

- **Difficulty:** Practitioner
- **Category:** Cross-site Scripting (XSS) - Reflected
- **Lab URL:** [Lab: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-double-quotes-encoded-single-quotes-escaped)
- **Date Solved:** 17/6/2026
## Vulnerability Summary

The app contains a reflected XSS vulnerability in the search functionality. The user-supplied input is inside a quoted string literal. Though it does attempt to perform HTML encoding with angle brackets and prevent input from breaking out of this string literal by escaping single quote characters with a backslash, we can supply our own backslash character to neutralize the backslash added by the app. Thus, we can still exploit XSS by breaking out of this existing string and injecting our own `JavaScript` statement.
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
- Trying to break out of the existing `JavaScript` string with the apostrophe (`'`) and inject own own payload with `';alert(1)//`, we get a response that reads:
```html
<script>
    var searchTerms = '\';alert(1)//';
    document.write('<img src="/resources/images/tracker.gif?searchTerms=' + encodeURIComponent(searchTerms) + '">');
</script>
```
The app automatically appends a backslash (`\`) to escape single quote characters, with the goal of preventing the input from breaking out of the `JavaScript` string. The backslash before a character tells the `JavaScript` parser that the character should be interpreted literally and not as a special character.
We need to escape the backslash character itself. We may be able to do this by supplying the input with our own backslash character.
## Exploitation Steps

1. Type in a random string into the search bar, e.g. `aaa`. Intercept this request.
2. Paste the payload below onto the `search` parameter and send request:
```
\';alert(1)//
```
3.  You should get a `200 OK` HTTP Response. Copy the response URL and open it in browser. The `alert()` function should trigger and lab is solved.
## Payload Used

`\';alert(1)//`
- The backslash character `\` neutralize the backslash that is automatically added by the app. This tricks the app into interpreting the second backslash literally, not as a special character, which means the quote is treated as a string terminator.
- The `'` breaks us out of the existing string literal.
- The statement terminator (`;`) ends the existing `var searchTerms = ''` statement. This helps us to introduce `alert(1)` to be executed as a standalone `JavaScript` statement.
- The `//` comments out the rest of the query, preventing an `Unterminated string literal` error.
## Root Cause

The app fails to properly escape user-supplied input when reflecting it directly into a JavaScript string context. By failing to use recursive backslash escaping (e.g., `\'`) or Unicode escapes for single quotes, an attacker can break out of the string literal and append malicious JavaScript statements.
## Remediation

The app must implement context-aware output encoding.
- **HTML Encoding:** Because the JavaScript is embedded within an HTML document, characters with special meaning in HTML (such as `<`, `>`, `&`, `"`, and `'`) must be converted to their corresponding HTML entities (e.g., `<` becomes `&lt;`).
- **JavaScript Unicode Escaping:** When reflecting untrusted data into a JavaScript string, use Unicode escapes for safety. For example, `<` should be encoded as `\u003c`. Modern web frameworks typically handle this automatically if data is passed to the DOM safely (e.g., via `textContent`), but server-side rendering requires strict encoding before the response is constructed.
- **JSON Serialization:** Pass the data through a JSON serializer on the server-side (e.g., `json_encode()` in PHP or `JSON.stringify()` in Node.js) before echoing it into the JavaScript execution context. This ensures all special characters, including quotes and backslashes, are strictly and safely escaped according to JSON string specifications, neutralizing any attempt to break out of the string literal.