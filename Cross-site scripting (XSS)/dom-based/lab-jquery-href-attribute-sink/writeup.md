## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - DOM-based
- **Lab URL:** [Lab: DOM XSS in jQuery anchor `href` attribute sink using `location.search` source](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-href-attribute-sink)
- **Date Solved:** 18/6/2026
## Vulnerability Summary

The app contains a DOM-based XSS vulnerability in the submit feedback page. The `jQuery` function extracts a parameter from the user-controllable URL through `window.location.search` and directly assigns it to the `href` attribute of a HTML element. Because of this, we can supply our `JavaScript` payload through the URL to exploit XSS.
## Reconnaissance

- Intercept the request to view the submit feedback page (`GET /feedback?returnPath=/`). The response body reads:
```html
 <script>
    $(function() {
	    $('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnPath'));
    });
</script>
```
The `jQuery`'s `attr()` function, which can change the attributes of DOM elements, is used to change the `href` attribute of a HTML element using unsanitized data from `location.search`. As this data is user-controllable, we can use this as our source to inject a `JavaScript` payload.
## Exploitation Steps

1. Intercept the request to view the submit feedback page: `GET /feedback?returnPath=/`
2. Change the value of the `returnPath` parameter to `javascript:alert(document.cookie)`, and send the request `GET /feedback?returnPath=javascript:alert(document.cookie)`
3. Observe that the lab is marked as solved on the browser.
## Payload Used

`javascript:alert(document.cookie)`
 As the `new URLSearchParams(...).get('returnPath')` parses the query string and extracts the specific string value of the `returnPath` parameter, injecting our payload to this parameter makes the `jQuery` selector sets its `href` attribute to our payload. When a victim clicks the `#backlink` element, the payload triggers.
## Root Cause

The input to the `returnPath` parameter is unvalidated before assignment. It allows `javascript:` instead of strictly enforcing `http(s):`.
## Remediation

- Ensure the `returnPath` is a relative URL, or validate it against a strict whitelist to prevent unexpected URIs or external domain redirects.