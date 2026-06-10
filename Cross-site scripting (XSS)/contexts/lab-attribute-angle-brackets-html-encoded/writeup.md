## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS)
- **Lab URL:** [Lab: Reflected XSS into attribute with angle brackets HTML-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-attribute-angle-brackets-html-encoded)
- **Date Solved:** 10/6/2026
## Vulnerability Summary

The app's search functionality is vulnerable to reflected XSS. It reflects user input from the `search` parameter into the `value` attribute of the search input. Though angle brackets are HTML-encoded, an attacker can inject additional attributes into the existing element and execute JavaScript through an event handler. Using `autofocus` with `onfocus` makes the payload execute without requiring the victim to interact with the page.
## Reconnaissance

- Entering a normal string like `aaa` into the search bar produces this request: `GET /?search=aaa`, and the string is reflected back in the response body inside a `<h1>` element: `<h1>0 search results for 'aaa'</h1>`. User input is being placed directly into the HTML without escaping.
- Injecting a tag such as `<script>alert(1)</script>` produces a `200 OK` HTTP Response, but does not trigger XSS because the application HTML-encodes angle brackets:
```html
&lt;script&gt;alert(1)&lt;/script&gt;
```
- Encoding angle brackets is insufficient for this context. Because the input is reflected inside an HTML tag attribute, we can remain inside the existing tag and inject new attributes instead of creating a new tag.
- The `onfocus` event handler executes JavaScript when the element receives focus. Adding `autofocus` causes the browser to focus the search input automatically when the page loads, so no user interaction is required.
## Exploitation Steps

1. Type in a random string into the search bar, e.g. `aaa`. Intercept this request.
2. Replace the `search` parameter's value with:
```
"%20autofocus%20onfocus%3Dalert(1)%20x%3D"
```
3. Send the request, then open the resulting URL in the browser. The browser automatically focuses the injected element, causing `onfocus=alert(1)` to execute. The alert dialog appears and the lab is solved.
## Payload Used

```
"%20autofocus%20onfocus%3Dalert(1)%20x%3D"
```

The payload is the URL-encoded version of:
```
" autofocus onfocus=alert(1) x="
```

| Character | URL-encoded (UTF-8) |
| --------- | ------------------- |
| space     | `%20`               |
| `=`       | `%3D`               |

- The `"` terminates the attribute value to introduce our new attribute. It is kept literal for this reason.
- `autofocus` instructs the browser to focus the search input automatically when the page loads.
- `onfocus=alert(1)` adds an event handler that executes JavaScript when the input receives focus.
- `x="` creates a trailing attribute that consumes the remaining characters from the original markup, keeping the resulting tag syntactically valid.
- The payload does not require angle brackets because it injects attributes into an element that already exists.
## Root Cause

The app reflects user-controlled input from the `search` parameter into an HTML attribute without applying context-appropriate attribute encoding. Encoding only angle brackets prevents attackers from injecting new tags, but it does not prevent them from injecting additional attributes and event handlers into the existing tag.
## Remediation

-  The application must treat the user-supplied input as data (instead of executable code) and HTML-entity encode it before reflecting it into the HTML document. Specifically, the following characters must be converted into their safe HTML entity equivalents:
    - `<` to `&lt;`
    - `>` to `&gt;`
    - `"` to `&quot;`
    - `'` to `&#x27;`
    - `&` to `&amp;`
- Avoid placing untrusted input into dangerous contexts where it can alter HTML attributes or event handlers.
- Implement a strict Content Security Policy (CSP) via HTTP response headers. Specifically, ensure the `script-src` directive is defined and explicitly omits the `'unsafe-inline'` keyword. Disallowing `'unsafe-inline'` completely prevents the browser from executing inline event handlers (such as the `onfocus` attribute used in this exploit), neutralizing the attack vector even if the HTML injection occurs.