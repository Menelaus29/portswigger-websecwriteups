## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - DOM-based
- **Lab URL:** [Lab: DOM XSS in `innerHTML` sink using source `location.search`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-innerhtml-sink)
- **Date Solved:** 18/6/2026
## Vulnerability Summary

The app contains a DOM-based XSS vulnerability in the search functionality. Client-side JavaScript reads the `search` parameter from `location.search` and assigns the value to an element's `innerHTML`. Because `innerHTML` parses the supplied value as HTML instead of treating it as text, we can inject a new element with an event handler and execute `JavaScript` in the victim's browser, exploiting XSS.
## Reconnaissance

- Entering a random string like `aaa` into the search bar produces this request: `GET /?search=aaa`. Inspecting the rendered page shows the search term being inserted into the DOM by client-side JavaScript, rather than being safely rendered as text by the server.
```html
<script>
	function doSearchQuery(query) {
        document.getElementById('searchMessage').innerHTML = query;
    }
    var query = (new URLSearchParams(window.location.search)).get('search');
    if (query) {
        doSearchQuery(query);
    }
</script>
```
The vulnerable script reads from the `location.search` source and writes the search term into a `div` using the `innerHTML` sink. This is dangerous because the browser interprets the assigned value as markup.
## Exploitation Steps

1. Search for a random value, e.g. `aaa`. Intercept this request. 
2. Replace the `search` parameter's value with the value below and send the request.
```
<iframe%20onfocus=alert(1)%20autofocus%20tabindex=1>
```
When you go onto the browser, lab should be marked as solved. You can open the response to the request onto the browser to trigger the payload, confirming XSS.
## Payload Used

```
<iframe%20onfocus=alert(1)%20autofocus%20tabindex=1>
```

The payload is a partially URL-encoded version of:
```html
<iframe onfocus=alert(1) autofocus tabindex=1>
```
- `<iframe>` creates a new HTML element when the value is assigned to `innerHTML`.
- `onfocus=alert(1)` adds an event handler that executes JavaScript when the `iframe` receives focus.
- `autofocus` causes the browser to focus the `iframe` automatically when it is inserted into the DOM.
- `tabindex=1` makes the `iframe` focusable and helps ensure the `onfocus` event fires without requiring user interaction.
- This works because `innerHTML` treats the search value as HTML markup. If the app used a text-only sink, the payload would be rendered as harmless text instead.
## Root Cause

The page contains a client-side taint flow from `location.search` to `innerHTML`. User-controlled input from the URL is inserted into the DOM as executable markup without sanitization or encoding. Because this processing happens in the browser, server-side reflection checks alone are not enough; the vulnerable JavaScript sink is what turns the URL parameter into active DOM nodes and event handlers.
## Remediation

- Replace `innerHTML` with a safe text sink such as `textContent` when rendering search terms:
```javascript
document.getElementById("searchMessage").textContent = search;
```
- Apply a strict Content Security Policy via HTTP response headers. Ensure the `script-src` directive omits `'unsafe-inline'` so inline event handlers such as `onfocus` cannot execute even if HTML injection occurs.
