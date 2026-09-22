## Metadata

- **Difficulty:** Apprentice
- **Category:** Information disclosure
- **Lab URL:** [Lab: Information disclosure in error messages](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-error-messages)
- **Date Solved:** 22/9/2026
## Vulnerability Summary

The app is vulnerable to information disclosure vulnerability in its `productId` parameter. Its verbose error messages reveal that it is using `Apache Struts 2 2.3.31`, an open-source framework that is vulnerable to RCE ([CVE-2017-5638](https://www.exploit-db.com/exploits/41570)).
## Reconnaissance

- The app is a simple online shop webapp. You can navigate to an item with the request `GET /product?productId=x`, with x being a number. Navigating to common endpoints like `/robots.txt`, `/sitemap.xml`, `/.DS_Store` or `/admin` all results in `404 Not Found` HTTP responses.
- As the lab's description stated, we need to find an instance where the app responses with a "verbose error messages".
## Exploitation Steps

1. Navigate to a random product (`GET /product?productId=1`).
2. Change the value of the `productId` parameter in the request line to a string of characters, e.g., `uia` (`GET /product?productId=uia`).
3. Observe that you received a `500 Internal Server Error` HTTP Response that reveals a `NumberFormatException` (since we submitted a string consists of characters instead of the expected number). At the end of the response body, the open source framework the app uses is leaked, `Apache Struts 2 2.3.31`:
```
HTTP/2 500 Internal Server Error
Content-Length: 1676

Internal Server Error: java.lang.NumberFormatException: For input string: "uia"
	at java.base/java.lang.NumberFormatException.forInputString(NumberFormatException.java:67)
	at java.base/java.lang.Integer.parseInt(Integer.java:661)
...

Apache Struts 2 2.3.31
```
4. Submit `2.3.31`. Lab is solved.
## Payload Used

`GET /product?productId=uia`
The app is not implemented to handle input strings that are not strictly numbers. It therefore throws an error.
## Root Cause

- **Improper Exception Handling / Verbose Debug Mode:** The web app and server environment are configured to display raw runtime stack traces directly to the end user upon an unhandled exception (`NumberFormatException`), rather than catching the error internally.
- **Lack of Input Validation / Type Checking:** The server attempts to cast the `productId` parameter directly to an integer without prior format validation through a regex or a `try-catch` block. When non-integer input is supplied, it causes an unhandled runtime error that bubbles up to the default error page, exposing internal stack traces, software components, and exact version numbers.
## Remediation

- Configure the app server (e.g., `web.xml` or framework-level error handlers) to handle HTTP `500` and unhandled exceptions globally, returning a uniform, generic error response (e.g., `An unexpected error occurred. Please try again later.`) without stack traces or environment metadata.
- Configure framework-specific debugging features (e.g., `struts.devMode = false` in `struts.xml`) to be disabled in production environments.
- Enforce strict type checking and validation on all user-supplied input before passing it into type-casting methods or database queries. Wrap type-parsing logic (such as `Integer.parseInt`) inside localized `try-catch` blocks and return a standard `400 Bad Request` or `404 Not Found` response upon failure.
- Log full stack traces and debugging metadata exclusively to secure, access-controlled internal server logs for debugging purposes.