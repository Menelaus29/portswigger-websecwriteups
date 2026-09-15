## Metadata

- **Difficulty:** Practitioner
- **Category:** Business logic vulnerabilities
- **Lab URL:** [Lab: Weak isolation on dual-use endpoint](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint)
- **Date Solved:** 15/9/2026
## Vulnerability Summary

A business logic flaw exists in the password change functionality where the app fails to securely isolate user contexts. The endpoint accepts an arbitrary user-controlled `username` parameter and processes the password update for that specific user, entirely bypassing the current password verification step if the `current_password` parameter is omitted from the request body. This allows an authenticated attacker to arbitrarily change the password of any user, including the administrator, resulting in full account takeover and privilege escalation.
## Reconnaissance

- Logging in with the provided credentials `wiener - peter`, we navigate to the account page to observe the password change workflow. Submitting a password change request generates a `POST /my-account/change-password` request.
- The request body contains four parameters:

```
csrf=[token]&username=wiener&current-password=peter&new-password-1=c&new-password-2=c
```
- Try deleting the value of the `current-password` parameter and sending a request with the body
```
csrf=[token]&username=wiener&current-password=&new-password-1=b&new-password-2=b
```
results in a HTTP Response that reads `Current password is incorrect`. However, deleting the entire parameter and sending:
```
csrf=[token]&username=wiener&new-password-1=b&new-password-2=b
```
, we were able to change the password successfully. This suggests that this `current-password` parameter is not evaluated if omitted. 
Furthermore, the inclusion of the `username` parameter in this request indicates that the backend is likely relying on client-supplied input to identify the target account rather than a secure, server-side session object.
## Exploitation Steps

1. Log into your account with the credentials `wiener - peter`.
2. Navigate to the account page and initiate a password change (`/my-account/change-password`).
3. Intercept the `POST /my-account/change-password` request with Burp Suite and send it to Repeater.
4. Modify the `username` parameter value to `administrator` and completely delete the `current-password` parameter and its corresponding value from the request body.
5. Set `new-password-1` and `new-password-2` to your desired password (e.g., `c`)
The final request body should look something like this: 
```
csrf=[token]&username=administrator&new-password-1=b&new-password-2=b
```
6. Forward the request to overwrite the administrator's password.
7. Log out, then log back in using the credentials `administrator - b`.
8. Navigate to the admin panel and delete the user `carlos`. Lab is solved.
## Payload Used

`csrf=[token]&username=administrator&new-password-1=b&new-password-2=b`

The app relies on the user-supplied `username` parameter to apply the database update instead of tying the action to the authenticated session token. Additionally, the backend validation logic for the current password is fundamentally flawed - it only verifies the password if the `current-password` parameter is explicitly present in the request. By omitting it, the app skips the check entirely and processes the password reset.
## Root Cause

The app trusts and relies on user-controllable input (`username`) to dictate the target of a sensitive state-changing action. Furthermore, the backend logic handling the password verification does not strictly verify the presence of the `current-password` parameter before allowing the update to execute.
## Remediation

- Remove the `username` parameter from the password change request. The backend must exclusively retrieve the target user's identity from the authenticated server-side session object.
- Implement strict input validation on the password change endpoint. Ensure that the `current-password` parameter is mandatory, and reject any request (e.g., returning a `400 Bad Request`) where this parameter is missing or empty.