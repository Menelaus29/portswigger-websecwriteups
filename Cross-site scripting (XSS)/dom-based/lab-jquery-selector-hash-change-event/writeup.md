## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - DOM-based
- **Lab URL:** [Lab: DOM XSS in jQuery selector sink using a hashchange event](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-selector-hash-change-event)
- **Date Solved:** 18/6/2026 
## Vulnerability Summary

The app contains a DOM-based XSS vulnerability in the homepage. It uses `jQuery`'s `$()` selector function to auto-scroll to a given post, whose title is passed via the `location.hash` property, in the event of `hashchange`. This means that we can deliver an exploit to force the victim's browser to load the page first, change the hash without user interaction (which fires `hashchange`), then trigger our XSS payload.
## Reconnaissance

Intercept the request to view the homepage (`GET /`). The response body reads:
```html
<script src="/resources/js/jquery_1-8-2.js"></script>
<script src="/resources/js/jqueryMigrate_1-4-1.js"></script>
<script>
    $(window).on('hashchange', function() {
	    var post = $('section.blog-list h2:contains(' + decodeURIComponent(window.location.hash.slice(1)) + ')');
        if (post) post.get(0).scrollIntoView();
	});
</script>
```
- The event listener waits for URL's fragment identifier (begins with `#`) to change to trigger the `hashchange` event.
- When the `hashchange` event fires, `location.hash.slice(1)` extracts the user-controllable fragment payload, stripping away the `#` character.
- The URL decoded payload (after `decodeURIComponent`) is concatenated directly into a `jQuery` selector string and passed to the `$()` function. The app's intention is to find a `h2` header containing this value to automatically scroll into it.
- As the app is using `jQuery` version `1.8.2`, the `$()` function can be our sink, as `jQuery` will parse and instantiate whatever HTML tags we insert into it.
## Exploitation Steps

1. Go to the exploit server.
2. Store this payload `<iframe src = "https://LAB-ID.web-security-academy.net/#" onload="this.src+='<img src=1 onerror=print()>'"></iframe>` and deliver exploit to victim.
3. Observe that lab is marked as solved. 
## Payload Used

`<iframe src = "https://LAB-ID.web-security-academy.net/#" onload="this.src+='<img src=1 onerror=print()>'"></iframe>`
- An inline frame is used on the exploit server to embed the victim's session of the app.
- The `onload` event waits until the `iframe` has completely finished loading the target's page. That way the `hashchange` event can be fired, and the payload can be executed.
- `this.src` accesses the current URL of the `iframe`, and the `+=` operator appends the XSS payload (`<img src=1 onerror=print()>`) directly to the end of the existing URL (ends in `#`).
## Root Cause

The vulnerability stems from passing user-controllable input (`window.location.hash`) directly into the jQuery `$()` selector function without validation or sanitization. In jQuery versions prior to `1.9.1` (the app uses `1.8.2)`, the `$()` function evaluates strings containing HTML tags and dynamically instantiates DOM elements. This allows an attacker to inject arbitrary HTML, including elements with malicious event handlers, which execute upon instantiation.
## Remediation

Upgrading jQuery to 1.9.1+ is a best practice but insufficient for this specific implementation. Because `window.location.hash.slice(1)` strips the leading `#`, an attacker can supply a payload starting with `<`. This bypasses jQuery 1.9+'s security checks, forcing the framework to parse the string as HTML rather than a selector.
To fix this, stop passing unsanitized user input directly into the `$()` selector function.
* Select the target elements first (e.g., all headers), then use jQuery's `.filter()` method to match their text content against the user input. This treats the input strictly as data rather than executable code.
* Enforce a whitelist (e.g., alphanumeric characters and hyphens only) on the hash value before processing it. 
* If concatenating user input into a selector string is unavoidable, sanitize the input using `CSS.escape()` to neutralize special characters, preventing them from being interpreted as HTML tags or malicious pseudo-classes.