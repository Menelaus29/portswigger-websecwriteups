## Metadata

- **Difficulty:** Practitioner
- **Category:** Cross-site Scripting
- **Lab URL:** [Lab: Reflected XSS into HTML context with all tags blocked except custom ones](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-all-standard-tags-blocked)
- **Date Solved:** 5/6/2026
## Vulnerability Summary

The app's search functionality is vulnerable to XSS. The application takes users' input from the `search` parameter and reflects it directly into the HTML document structure (inside the `<h1>` tag). Though it does attempt to block all tags, custom ones along with all attributes are still allowed, enabling us to exploit XSS through `onfocus`.
## Reconnaissance

- Entering a normal string like `aaa` into the search bar produces this request: `GET /?search=aaa`, and the string is reflected back in the response body inside a `<h1>` element: `<h1>0 search results for 'aaa'</h1>`. User input is being placed directly into the HTML without escaping.
- Trying to inject `<script>alert(1)</script>` to the search parameter, we get a `400 Bad Request` HTTP response that reads `"Tag is not allowed"`. We need to find tags and attributes that are allowed.
## Exploitation Steps

1. Type in a random string into the search bar, e.g. `aaa`. Intercept this request.
2. Send this request to Burp Intruder (or the Automate tab in Caido). Modify the header of the request to `GET /?search=<> HTTP/2` and add payload position between the angle brackets (`GET /?search=<$$> HTTP/2`). Paste the tags on [XSS Cheatsheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) onto the list of payloads to be used. Select attack type to be `Sniper Attack`, then start attack.
3. Once the attack's done, sort the status code of the requests - as we must find request(s) with status code of 200, signifying that the tag is allowed. You should see there is only one type of tag allowed, custom tags (represented by the `<xss>` tag).
4. Next, we need to find out what type(s) of attribute is allowed. Modify the header of request to `GET /?search=<xss%20$$=1> HTTP/2` (`$$` is the payload position) and copy the events on  [XSS Cheatsheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) to be the payload list. Run a `Sniper Attack` again. After the attack's done, you should see that all types of attributes are allowed.
5. Per the lab's request "Your solution must not require any user interaction. Manually causing `print()` to be called in your own browser will not solve the lab", we must use an event that does not require any user interaction. Use the filter on the [XSS Cheatsheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) to find payloads that suit this task. After trial and error, I landed on the `onfocus(autofocus)`tag.
6. Go to the exploit server and paste this payload onto the body:
```js
<script>
window.location = "https://YOUR-LAB-ID.web-security-academy.net/?search=%3Cxss%20onfocus=alert(document.cookie)%20autofocus%20tabindex%3D1%3E"
</script>
```
Then Store -> Deliver exploit to victim. You should see that the lab is solved.
## Payload Used

[XSS Cheatsheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
```js
<script>
window.location = "https://YOUR-LAB-ID.web-security-academy.net/?search=%3Cxss%20onfocus=alert(document.cookie)%20autofocus%20tabindex%3D1%3E"
</script>
```

| Character | URL-encoded (UTF-8) |
| --------- | ------------------- |
| <         | %3C                 |
| =         | %3D                 |
| >         | %3E                 |
| space     | %20                 |
The payload (injected into the `search` parameter) is this string URL-encoded:
`<xss onfocus=alert(document.cookie) autofocus tabindex=1>`
- The `onfocus` event fires when a element has focus. When it fires, `alert(document.cookie)` is triggered.
- The `autofocus` attribute is used to focus automatically, triggering `onfocus`.
- The `tabindex=1` attribute forces the custom `<xss>` tag to become a focusable element in the DOM, which is required for the `onfocus` event to trigger."
## Root Cause

The app takes untrusted input from the `search` parameter and reflects it directly into the HTML document structure (inside the `<h1>` tag).

Additionally, the app insecurely relies on a WAF as the primary defense mechanism against XSS. The WAF was configured with a flawed blocklist that failed to account for custom tags and their attributes.
## Remediation

-  The application must HTML-entity encode all user-supplied input before reflecting it into the HTML document. Specifically, the following characters must be converted into their safe HTML entity equivalents:
    - `<` to `&lt;`
    - `>` to `&gt;`
    - `"` to `&quot;`
    - `'` to `&#x27;`
    - `&` to `&amp;`
- Implement strict a CSP Level 2 policy with Google Universal's `strict-dynamic` via HTTP response headers to mitigate the impact of any missed injection flaws. 