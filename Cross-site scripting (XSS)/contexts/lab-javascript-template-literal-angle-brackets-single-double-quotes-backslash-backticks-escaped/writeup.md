## Metadata

- **Difficulty:** Practitioner
- **Category:** Cross-site Scripting (XSS) - Reflected
- **Lab URL:** [Lab: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped)
- **Date Solved:** 17/6/2026
## Vulnerability Summary

The app contains a reflected XSS vulnerability in the search functionality. The user-supplied `search` parameter is reflected inside a JavaScript template literal. Though the app attempts to prevent common JavaScript-string breakouts by escaping angle brackets, quotes, backslashes, and backticks, it does not prevent template literal expression interpolation. This allows us to inject `${alert(1)}` and have the JavaScript engine evaluate it inside the existing template string.
## Reconnaissance

- Entering a normal string like `aaa` into the search bar produces this request: `GET /?search=aaa`, and the string is reflected back in the response body inside a JavaScript template literal:
```html
<script>
    var message = `0 search results for 'aaa'`;
    document.getElementById('searchMessage').innerText = message;
</script>
```
- Trying to break out of the existing JavaScript context with payloads that use angle brackets, quotes, backslashes, or backticks does not work because those characters are escaped or encoded by the app.
- The important detail is that the reflection is already inside a template literal, which is delimited by backticks. In `JavaScript` template literals, `${...}` is not treated as plain text. The expression inside the curly braces is evaluated by the JavaScript engine.
- Since the app does not neutralize `${` and `}`, we do not need to break out of the template literal. We can execute `JavaScript` from inside it.
## Exploitation Steps

1. Type in a random string into the search bar, e.g. `aaa`. Intercept this request.
2. Replace the `search` parameter's value with:
```
${alert(1)}
```
3. Send the request, then copy the resulting URL and open it in the browser. The browser evaluates the expression interpolation inside the template literal, causing `alert(1)` to execute and the lab to be solved.
## Payload Used

```
${alert(1)}
```
- `${...}` starts a template literal expression interpolation.
- `alert(1)` is placed inside that interpolation, so it is evaluated as JavaScript instead of being treated as a search string.
## Root Cause

The app reflects user-controlled input from the `search` parameter directly into a JavaScript template literal without applying JavaScript-context output encoding. Escaping quotes and backticks is insufficient for template literals because `${...}` has special meaning inside them. Any untrusted data inserted into a template literal must also prevent expression interpolation from being parsed as code.
## Remediation

The app must implement context-aware output encoding.
- **JavaScript Unicode Escaping:** When reflecting untrusted data into a JavaScript string or template literal, encode characters with JavaScript syntax meaning, including `$`, `{`, `}`, `<`, `>`, quotes, backslashes, and backticks. For example, `<` should be encoded as `\u003c`.
- **JSON Serialization:** Pass the data through a safe JSON serializer before inserting it into JavaScript. Avoid manually concatenating or interpolating user input into executable script blocks.
- **Safe DOM APIs:** Avoid generating JavaScript code from user input. Put user-controlled text into the page with safe APIs such as `textContent` after the script has loaded.
- **Content Security Policy:** Implement a strict CSP that prevents inline script execution where possible. CSP should be treated as defense-in-depth, not as the primary fix.
