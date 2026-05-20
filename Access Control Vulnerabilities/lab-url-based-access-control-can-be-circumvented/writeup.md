## Metadata

- **Difficulty:** Practitioner
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: URL-based access control can be circumvented](https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented)
- **Date Solved:** 20/5/2026
## Vulnerability Summary

The app suffers from Broken Access Control. Though the app evaluates the path supplied in the request line in order to deny access to certain endpoints, the app improperly trusts the non standard `X-Original-URL` header over the actual request path. This allows us to vertically escalate our privilege by tricking the backend into processing the restricted endpoint, bypassing the frontend's access rules.
## Reconnaissance

Accessing the unauthorized admin panel at `/admin` right away will yield a `403 Forbidden` HTTP Response with "Access denied" in the body. However, per the lab description, we know that the front end is implemented to be block external access to the `/admin` path, but the backend app is built on a framework that supports the `X-Original-URL` header. If the app implicitly trusts this header over the actual request line, we can use it to send requests to the authorized endpoint `/admin`, which we need to delete user `carlos`.
## Exploitation Steps

1. Navigate to `url/admin` and intercept this request.
2. In the intercepted request, modify the request headers as follows:
```
GET / HTTP/1.1
X-Original-URL: /admin/
...
```
and send the request. You should get a `200 OK`, and access to the admin panel. We see that the path to delete user `carlos` is `/admin/delete?username=carlos`.
3. Modify the intercepted request headers as follows:
```
GET /?username=carlos HTTP/1.1
X-Original-URL: /admin/delete
...
```
and send the request. You should get a `302 Found` and `Location: /admin` HTTP Response. Go on the website, and observe that lab is solved.
## Payload Used

To get the path for deleting `carlos`:
```
GET / HTTP/1.1
X-Original-URL: /admin
```
To delete `carlos`:
```
GET /?username=carlos HTTP/1.1
X-Original-URL: /admin/delete
```
The `X-Original-URL` is typically used to tell the backend app which URL the client originally requested before an intermediary (frontend server or proxy) modified it. In this lab, it is used to override the default request path.
## Root Cause

The backend framework supports and blindly trusts the value of the user-controllable header `X-Original-URL` instead of the actual request URL or the authenticated session data. Thus, even though the frontend server is implemented to block access to restricted paths (`/admin`), supplying the request with `X-Original-URL` completely bypasses this defense mechanism. 
## Remediation

- Enforce mandatory, **server-side** access control checks within the application logic (e.g. through session tokens) on every request to a sensitive endpoint in order to verify the user's role and their privileges.
- Unset/Ignore the `X-Original-URL` and `X-Rewrite-URL` headers completely. Configure the frontend reverse proxy or load balancer to aggressively strip/drop these headers before routing the request to the backend application. 