## Metadata

- **Difficulty:** Apprentice
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: User role controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter)
- **Date Solved:** 21/4/2026
## Vulnerability Summary

The app determines the user's access rights and role at login using a cookie. However, the application relies entirely on this client-controllable cookie for authorization, allowing for a simple modification to gain administrative privileges.
## Reconnaissance

- Navigating to `url/admin` before logging in, we get a `401 Unauthorized` HTTP response that reads "Admin interface only available if logged in as an administrator". There's no modifiable field in the request that might bypass this check.
- However, after logging in with the credentials `wiener - peter`, modifying the URL to `url/admin` also gives us a `401 Unauthorized` HTTP response with the same message, but this time there is an `Admin=false` cookie field and value in the request: `Cookie: session=sessionstring; Admin=false`. We might be able to modify the value of this field to bypass role check and gain administrative privileges.
## Exploitation Steps

1. Log in with the credentials `wiener - peter` (given by the lab).
2. Modify the URL parameter from `url/my-account?id=wiener` to `url/admin`. Intercept this request with Burp Suite proxy.
3. Change the value of the `Admin` cookie field from `false` to `true`. You should get a HTTP response with a status code of `200 OK` that reads "Admin panel" and the options to delete users like this:
```HTML
<div>
	<span>
		wiener - 
	</span>
	<a href="/admin/delete?username=wiener">
		Delete
	</a>
</div>
<div>
    <span>
	    carlos - 
    </span>
    <a href="/admin/delete?username=carlos">
	    Delete
	</a>
</div>
```
4. In Burp Repeater, modify the request path to `GET /admin/delete?username=carlos HTTP/2` while ensuring the `Cookie: Admin=true` header remains injected. Send the request.
5. Observe that you get a `302 Found` HTTP response that signifies a redirection. Go on to the lab's website, and you shall see that lab is solved.
## Payload Used

Cookie: `Admin=true`.
Modifying this header bypasses the client-side's trust assumption, granting access and rights to the `/admin` routing matrix. The idempotent `GET` HTTP method works here because of the app's insecure implementation of state-changing action for `GET`'s request.
## Root Cause

The app implements a cookie to determine user's access rights and role at login for protection of sensitive functionality. However, the application implicitly trusts client-side provided state without server-side validation or cryptographic integrity, thus allowing us to gain administrative privileges simply by modifying the value of the check cookie.
## Remediation

Implement mandatory, server-side access control checks (e.g. through session tokens) on every request to a sensitive endpoint in order to verify the user's role and their privileges. Never implement these checks client-side. Deny access if there are attempts of privilege escalation.