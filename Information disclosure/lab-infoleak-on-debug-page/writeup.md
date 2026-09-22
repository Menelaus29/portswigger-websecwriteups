## Metadata

- **Difficulty:** Apprentice
- **Category:** Information disclosure
- **Lab URL:** [Lab: Information disclosure on debug page](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-on-debug-page)
- **Date Solved:** 22/9/2026
## Vulnerability Summary

The app is vulnerable to the information disclosure. Its client-side code reveals the debug path, `/cgi-bin/phpinfo.php`, that contains the `SECRET_KEY` environment variable.
## Reconnaissance

- The app is a simple online shop webapp. You can navigate to an item with the request `GET /product?productId=x`, with x being a number. Navigating to common endpoints like `/robots.txt`, `/sitemap.xml`, `/.DS_Store` or `/admin` all results in `404 Not Found` HTTP responses.
- Try submitting a non-integer input (`uia`) in the `productId` parameter returns a `400 Bad Request` that reads `"Invalid product ID"`. Submitting other characters like `/`, `'`, `<`,... results in the same response.
- Submitting a `productId` value that is not available (`GET /product?productId=67`) returns a `404 Not Found` HTTP Response.
- Viewing the raw client-side code of the app (`view-source:ttps://lab-id.web-security-academy.net/`) reveals a commented line that contains the debug path:
```
<!-- <a href=/cgi-bin/phpinfo.php>Debug</a> -->
```
We are able to visit this endpoint.
## Exploitation Steps

1. Navigate to the endpoint `/cgi-bin/phpinfo.php`. You should receive a `200 OK` HTTP Response, and now have access to the app's comprehensive information about its server PHP configuration.
2. Search for the keyword `SECRET_KEY` in the response. Submit the value of this environment variable (`POST /submitSolution`). Lab is solved.
## Payload Used

`GET /cgi-bin/phpinfo.php`
The app leaks the debug path in the client-side code, and the endpoint, which contains sensitive information (in this case, the `SECRET_KEY` environment variable) is accessible for anyone.
## Root Cause

The web app server exposes a development/diagnostic script (`phpinfo()`) within a publicly accessible web root directory (`/cgi-bin/`). Additionally, sensitive deployment references were left commented out in production client-side HTML, allowing any user to discover secret environment variables (`SECRET_KEY`).
## Remediation

- Delete or disable all debugging scripts and files calling `phpinfo()` or similar diagnostic functions from production environments.
- If diagnostic endpoints are required for operations, enforce strict network-level controls (e.g., restricting access to `127.0.0.1` or internal VPN CIDR blocks) and require administrative authentication.
- Remove internal paths and developer comments from client-side templates before deployment.
- Store and manage secrets using a dedicated secrets manager or ensure web-accessible runtime diagnostics cannot dump process environment tables (`$_SERVER` / `$_ENV`).