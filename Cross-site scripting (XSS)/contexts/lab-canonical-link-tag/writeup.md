## Metadata

- **Difficulty:** Practitioner
- **Category:** Cross-site Scripting (XSS) - Reflected
- **Lab URL:** [Lab: Reflected XSS in canonical link tag](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-canonical-link-tag)
- **Date Solved:** 11/6/2026
## Vulnerability Summary

The app contains a reflected XSS vulnerability in the canonical link tag. It reflects the URL's query string inside the canonical link's single-quoted `href` attribute. Though angle brackets are HTML-encoded, an attacker can use a single quote to terminate the `href` value and inject the `accesskey` and `onclick` attributes. When the victim presses the assigned access key in Chrome, the browser invokes the injected event handler and executes JavaScript.
## Reconnaissance

- Navigate to the home page with an arbitrary query string, e.g. `/?aaa`, and intercept the request. The query string is reflected in the response inside the canonical link tag:
```html
<link rel="canonical" href='https://YOUR-LAB-ID.web-security-academy.net/?aaa'/>
```
- Trying to inject a new tag does not work because the app HTML-encodes angle brackets.
- The `href` value is enclosed in single quotes, but single quotes in the query string are not HTML-encoded. We can use a single quote to terminate the `href` value and inject additional attributes into the existing `<link>` tag.
## Exploitation Steps

1. Navigate to the following URL: `url/?%27accesskey=%27X%27onclick=%27alert(1)`. Lab is marked as solved automatically.
2. Additionally, you can trigger the `alert()` function in your own browser with these key combinations:
```
Windows: Alt + Shift + X (Firefox/Chrome), Alt + X (Edge)
MacOS: Ctrl + Alt + X
Linux: Alt + X
```
## Payload Used

```
%27accesskey=%27X%27onclick=%27alert(1)
```

The payload is the URL-encoded version of:
```
'accesskey='X'onclick='alert(1)
```

| Character | URL-encoded (UTF-8) |
| --------- | ------------------- |
| `'`       | `%27`               |

- The first `'` terminates the canonical link's existing `href` attribute value.
- `accesskey='X'` assigns the `X` key as an access key for the canonical link element.
- `onclick='alert(1)` adds an event handler that executes JavaScript when Chrome activates the element through the access key.
- The quote already present in the original markup closes the injected `onclick` attribute value.
## Root Cause

The app constructs the canonical link using the user-controlled query string and reflects it into a single-quoted HTML attribute without applying context-appropriate attribute encoding. Encoding only angle brackets prevents attackers from injecting new tags, but failing to encode single quotes allows them to terminate the `href` value and inject event-handler attributes into the existing tag.
## Remediation

- Construct the canonical URL from trusted server-side values and exclude untrusted query-string data unless it is strictly required.
- Apply context-aware HTML attribute encoding before placing any user-controlled value into an attribute. At minimum, encode `'` as `&#x27;`, along with `"`, `<`, `>`, and `&`.
- Implement a strict Content Security Policy (CSP) via HTTP response headers. Ensure the `script-src` directive omits the `'unsafe-inline'` keyword so inline event handlers such as `onclick` cannot execute even if attribute injection occurs.
