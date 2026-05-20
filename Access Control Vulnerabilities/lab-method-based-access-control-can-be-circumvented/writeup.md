## Metadata

- **Difficulty:** Practitioner 
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: Method-based access control can be circumvented](https://portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented)
- **Date Solved:** 20/5/2026
## Vulnerability Summary

The app is vulnerable to Broken Access Control. Though it does implement access controls based on the HTTP method of requests (as in, restricting certain methods to certain endpoints), this mechanism is bypassable since the app allows for different HTTP methods to perform the same action. Using this, we can vertically escalate our privileges.
## Reconnaissance

Navigating to `url/login` and logging in with credentials `administrator - admin`, we are met with an admin panel with options to upgrade/downgrade 2 users (excluding admin), `carlos` and `wiener` from `NORMAL` to `ADMIN` and vice versa. Intercept the request to upgrade `carlos`, we see that the intercepted request looks like:
```
POST /admin-roles HTTP/1.1

...

username=wiener&action=upgrade
``` 
Now, after logging out of the administrator account and logging in to the wiener's account (`wiener - peter`), we have a new session cookie value that belongs to the user `wiener`. Using the template in the intercepted request and `wiener`'s session cookie value and changing the body to `username=wiener&action=upgrade` yields a `401 Unauthorized` HTTP Response when sent. However, changing the HTTP method to a different one than `POST` gets us a `400 Bad Request` and `Missing parameter 'username'` in the response body. This suggests that the app only guards against `POST` requests at the `/admin-roles` endpoint, and we may be able to use other methods to perform actions on this endpoint.
## Exploitation Steps

1. Navigate to `url/login` and login with the credentials `administrator - admin`.
2. Intercept the request to upgrade `carlos` from a `NORMAL` to an `ADMIN` user.
3. Log out, and log in with credentials `wiener - peter`.
4. Intercept any request made in `wiener`'s account to get `wiener`'s session cookie value. Copy this value, and paste it onto the intercepted request on step 2.
5. On the last line, change the value of the `username` parameter to `wiener`: `username=wiener&action=upgrade`, then change the request method to `GET` (right click on the request -> `Toggle GET/POST` , or do this manually by performing a normal `GET` request in wiener's account to get the template). The modified request should have the HTTP header of `GET /admin-roles?username=wiener&action=upgrade HTTP/1.1`. Send the request. 
6. Observe that you received a `302 Found` HTTP Response.  Go on the website, and observe that lab is solved.
## Payload Used

HTTP header: `GET /admin-roles?username=wiener&action=upgrade HTTP/1.1`
Since the app tolerates different HTTP request methods when performing users' privilege upgrading but, insecurely, does not restrict all of the methods that can be used to perform this action, we can take advantage of this and perform a `GET` request that is equivalent to a `POST` request to upgrade our privileges.
## Root Cause

The application implements method-specific access control checks by verifying admin session cookies strictly for `POST` requests to `/admin-roles`. However, the underlying routing framework maps multiple HTTP methods (`GET`, `POST`) to the same controller logic. This mismatch allows an attacker to bypass the access control middleware by issuing a `GET` request, while the back-end controller still processes the parameters and executes the state-changing action.
## Remediation

- Enforce access control checks at the controller or application logic layer, ensuring they are independent of the HTTP method used.
- Strictly adhere to RESTful principles by rejecting inappropriate HTTP methods for state-changing operations. The `/admin-roles` endpoint must return a `405 Method Not Allowed` for any method other than `POST` or `PUT`.
- Implement routing configurations that map specific HTTP methods to specific endpoints explicitly, rather than relying on catch-all routing mechanisms.