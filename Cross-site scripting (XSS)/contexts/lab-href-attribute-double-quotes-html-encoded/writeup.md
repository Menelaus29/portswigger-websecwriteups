## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - Stored
- **Lab URL:** [Lab: Stored XSS into anchor `href` attribute with double quotes HTML-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-href-attribute-double-quotes-html-encoded)
- **Date Solved:** 11/6/2026
## Vulnerability Summary

The app contains a stored XSS vulnerability in the comment functionality. Specifically, the content of the user's website is stored inside a `href` attribute of a rendered anchor tag. This allows us to inject a URI scheme that evaluates `JavaScript`, exploiting XSS.
## Reconnaissance

View a post (`url/post?postId=7`) and submit a comment using random values (note that you will have to use the suffix `@gmail.com` for the `email` parameter). After that, intercept the request to go that same post. On the response body, we see that our supplied input of the `website` parameter is stored directly inside a `href` attribute.
```
<section class="comment">
    <p>
        <img src="/resources/images/avatarDefault.svg" class="avatar"> <a id="author" href="testwebsite">test name</a> | 11 June 2026
    </p>
    <p>test comment</p>
    <p></p>
</section>
```
We can inject an URI scheme that executes `JavaScript` into this parameter.
## Exploitation Steps

1. Navigate to a random post, e.g. `url/post?postId=1`.
2. Input these values and submit the comment. Note that other than the value for the `website` parameter, the other values can be anything (as long as you have the suffix `@gmail.com` with the value of the `email` parameter).
```
Comment: a
Name: b
Email: c@gmail.com
Website: javascript:alert(1)
```
3. After submitting the comment, the lab will be automatically marked as solved. You can go back to the page of the post and click on the author name of our comment to invoke the `alert()` function in our browser.
## Payload Used

`javascript:alert(1)`
- The URI scheme `javascript:` allows code to be executed directly when a browser attempts to navigate to a URL.
- When the simulated victim clicks on the author name, the `alert(1)` function is called.
## Root Cause

The appl HTML-encodes user input, preventing escapes from the `href` attribute. However, it fails to parse and validate the URI scheme of the provided URL. Because the input is rendered directly into the `href` attribute, an attacker can supply a malicious URI scheme (like `javascript:`) to execute arbitrary code.
## Remediation

Implement strict server-side validation on the `website` parameter:
- Use an established URL parsing library to extract the protocol/scheme from the user's input.
- Implement an strict whitelist of safe protocols (exclusively `http://` and `https://`).
- Reject the request entirely or neutralize the input (e.g., prefixing with `http://`) if it utilizes dangerous schemes such as `javascript:`, `data:`, or `vbscript:`.