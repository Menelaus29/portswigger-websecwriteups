## Metadata

- **Difficulty:** Apprentice
- **Category:** Cross-site Scripting (XSS) - Stored
- **Lab URL:** [Lab: Stored XSS into HTML context with nothing encoded](https://portswigger.net/web-security/cross-site-scripting/stored/lab-html-context-nothing-encoded)
- **Date Solved:** 24/5/2026
## Vulnerability Summary

The blog comment functionality stores user input and renders it back into the page without HTML encoding. Submitting a `<script>` tag in the comment field causes the payload to be persisted in the database and executed in every visitor's browser whenever the blog post is viewed, making this a stored (persistent) XSS vulnerability.
## Reconnaissance

- Submitting a normal comment on a blog post shows the comment appearing on the page after submission. The comment body is reflected verbatim in the HTML source between `<p>` tags with no encoding applied.
- Testing `<b>test</b>` in the comment body shows the text rendered in bold in the browser, confirming that HTML tags in comments are not stripped or encoded before being inserted into the page.
## Exploitation Steps

1. Navigate to any blog post on the lab.
2. Fill in the comment form with any values for Name, Email, and Website, and enter `<script>alert(1)</script>` as the comment body.
3. Submit the comment.
4. Navigate back to the blog post (or reload it). The stored payload executes, triggering an `alert(1)` dialog. The lab is solved.
## Payload Used

`<script>alert(1)</script>`
Unlike reflected XSS, the payload is stored server-side and injected into every page render of the blog post. When any user (including the attacker themselves, or a victim tricked into visiting the post) loads the page, the browser encounters the `<script>` block and executes it as JavaScript. The impact is broader than reflected XSS because no victim interaction with a crafted URL is required — simply visiting the page is enough.
## Root Cause

The comment body is stored and later retrieved from the database and inserted into the HTML response without output encoding.
## Remediation

HTML-encode all stored user content on output, before inserting it into any HTML context:
````python
from markupsafe import escape

comment_body = escape(stored_comment)
html = f"<p>{comment_body}</p>"
````
Additionally, consider a Content Security Policy (CSP) with `script-src 'self'` as a defence-in-depth measure to block inline script execution even if encoding is ever missed.
