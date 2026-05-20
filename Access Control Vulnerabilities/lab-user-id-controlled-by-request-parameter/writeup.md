## Metadata

- **Difficulty:** Apprentice
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: User ID controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter)
- **Date Solved:** 20/5/2026
## Vulnerability Summary

The app uses username to identify users, allowing them to access their page using an URL like: `url/my-account?id=username`. It does not implement any checks regarding the identity of the user accessing a `my-account` endpoint, leading to a **Insecure Direct Object Reference** (IDOR) vulnerability which allows horizontal privilege escalation, granting us access to any arbitrary user given their username.
## Reconnaissance

Logging in with the credentials `wiener - peter` (provided by the lab) ,we are taken to `url/my-account?id=wiener`. Changing this to `url/my-account?id=carlos` yields a `200 OK` HTTP Response and takes us straight to `carlos`'s account page, bypassing all authorization mechanisms.
## Exploitation Steps

1. Navigate to `url/login` and login with the credentials `wiener-peter`.
2. On `url/my-account?id=wiener`, go to the URL `url/my-account?id=carlos`
3. You should be in `carlos`'s account with their API key. Copy this key and submit solution. Lab is solved.
## Payload Used

`/my-account?id=carlos`.
Modifying the value of the `id` parameter to another user grants access to that user even if their login credentials are unknown. 
## Root Cause

The app fails to enforce context-dependent access controls on the backend. It implicitly trusts user-supplied input to perform data-fetching operations without verifying if the server-side session mapping corresponds to the requested `id`.
## Remediation

- When rendering the "My Account" page or returning sensitive data, the application should drop the `id` parameter entirely from the request. Instead, it should extract the user's identity directly from the authenticated session object (e.g., the server-side session store mapped to the user's session cookie) and fetch the corresponding data.
- If passing the user ID via a parameter is strictly required by the application's architecture, the backend must explicitly verify authorization before returning data. The server must check if the ID of the currently authenticated user (derived from their session token) matches the ID supplied in the request parameter. If they do not match, the application must return an `HTTP 403 Forbidden` or `HTTP 401 Unauthorized` response.

