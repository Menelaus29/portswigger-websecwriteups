## Metadata

- **Difficulty:** Practitioner
- **Category:** SSRF
- **Lab URL:** [Lab: Blind SSRF with out-of-band detection](https://portswigger.net/web-security/ssrf/blind/lab-out-of-band-detection)
- **Date Solved:** 13/8/2026
## Vulnerability Summary

The app is vulnerable to Server-side Request Forgery (SSRF) via the `Referer` header used in its analytics tracking functionality. Because the backend fetches the URL in this header when a product page is loaded with no further validation or sanitization, an attacker can force the server to make arbitrary OOB (HTTP) requests.
## Reconnaissance

Per the lab's description: "This site uses analytics software which fetches the URL specified in the Referer header when a product page is loaded." Not much else needed to be confirm - the `Referer` header is the injection point. 
## Exploitation Steps

1. Navigate to a product page (`/product?productId=1`). Intercept this request with Burp Suite.
2. Modify the `Referer` header to point to your generated Burp Collaborator payload (`https://[id].oastify.com`).
3. Forward the request and observe the Burp Collaborator client. It will log incoming DNS lookups and HTTP requests originating from the application's backend server. Lab is automatically marked as solved.
## Payload Used

`Referer: https://[id].oastify.com`
Since the backend server blindly parses the `Referer` header and issues an HTTP GET request to the supplied domain to log referral data, changing the URL in the `Referer` header helps the Collaborator server captures this interaction, proving the server can be coerced into making outbound network connections to arbitrary external domains.
## Root Cause

The app trusts user-controlled input (the `Referer` header) and passes it directly to a backend HTTP fetching mechanism without proper validation, sanitization, or enforcing an whitelist.
## Remediation

Do not implicitly trust the `Referer` header. If the app requires fetching external resources based on user input, validate the URL against a whitelist of permitted IP addresses/ domains. Additionally, disable the backend HTTP client's ability to follow redirects and restrict its egress network access to only explicitly required external services.