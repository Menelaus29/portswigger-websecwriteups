## Metadata

- **Difficulty:** Apprentice
- **Category:** Authentication
- **Lab URL:** [Lab: 2FA simple bypass](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass)
- **Date Solved:** 16/4/2026
## Vulnerability Summary

The application implements 2FA insecurely by fully authenticating the user session immediately after the first authentication factor (username and password) is verified. The secondary 2FA verification step is implemented merely as a routing barrier, meaning an attacker with valid primary credentials can bypass the 2FA prompt entirely via forced browsing to authenticated endpoints.
## Reconnaissance

 - When logging in with our given credentials `wiener` - `peter`, when prompted to type the security code, if we click on the "Back to lab home" button next to the "Email client" button on the header of the website then click on the "My Account" in the homepage, you will see that we're logged in, completely bypassing the 2FA. 
## Exploitation Steps

1.  Navigate to `url/login` and type in the credentials `carlos` - `montoya`. Click on "Log in". You will be redirected to `url/login2`, where you are prompted to type in the 4-digit security code. 
2. Without submitting the code, manually change the URL to `url/my-account?id=carlos`. You should see that you are logged in. Lab is solved.
## Payload Used

`/my-account?id=carlos` 
## Root Cause

The business logic flaw lies in the session management lifecycle. The application issues a fully privileged session token (cookie) immediately upon successful verification of the username and password. The application fails to enforce a restricted "pending 2FA" state on the server side, thus allows the bypass of this factor.
## Remediation

Upon successful first-factor authentication (through login credentials), the server should issue a temporary, restricted session token (or flag the current session state as `pending_2fa`). This restricted state must explicitly deny access to all protected resources and only permit interaction with the 2FA verification endpoint. The session must only be upgraded to a fully authenticated state after the secondary authentication factor is successfully authenticated.