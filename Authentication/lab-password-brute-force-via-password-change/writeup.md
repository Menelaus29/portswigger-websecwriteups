## Metadata

- **Difficulty:** Practitioner
- **Category:** Authentication
- **Lab URL:** [Lab: Password brute-force via password change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change)
- **Date Solved:** 6/5/2026
## Vulnerability Summary

The vulnerability is **Information Disclosure via Verbose Error Messages**. Specifically, the app explicitly tells the user (and in this case the attacker) whether a password for an account is correct in the password change functionality by returning either `Current password is incorrect` or `New passwords do not match`. Additionally, the password change functionality implicitly trusts user controllable input and does not have any defense mechanisms against brute force attacks. All of this allow us to enumerate the login credentials for an arbitrary user, `carlos` in this case.
## Reconnaissance

After navigating to `url/login` and log in with credentials `wiener - peter` (given by the lab), you'll be taken to `url/my-account?id=wiener`. On this page, you should see that there's a password change functionality, where you are able to input your current password, a new password and the confirmation for this new password.
- If you input your correct current password `peter`, then validly change it to something else, on the first attempt, you should see a `Password changed successfully!` response. However, on the second attempt, you will be logged out and taken to the `url/login` page. Try logging in immediately will yield the message `You have made too many incorrect login attempts. Please try again in 1 minute(s).`
- If you deliberately input the wrong current password, then 2 matching values for the new password, the app will return `Current password is incorrect`. You can do this for however many times you like without getting rate limited.
- If you deliberately input the wrong current password, then 2 values that do **NOT** match for the new password, the app will return `New passwords do not match`. Similarly, you can do this for however many times you like without getting rate limited.
Also, the request to change password has a hidden field `username=wiener`. Try changing the value of this field to `carlos` yields a `200 OK` with no errors.
All these information suggest we can enumerate the password for any arbitrary user.
## Exploitation Steps

1. Navigate to `url/login` and login with credentials `wiener - peter`.
2. Intercept the request to change password, after you have inputted the **wrong** current password and 2 different, non - matching values for the new password.
3. Modify the `username` field to `username=carlos`. Change the value of the `Referer` header to `url/my-account?id=carlos`.
4. Select the payload position at the `current-password` field. Paste the [Candidate password list](../candidatepasswords.txt) (provided by the lab), then start a brute force attack on this position.
5. After the attack's finished, search for the response that contains the message `New passwords do not match` by configuring the `HTTPQL` query to `resp.raw.cont:"match"`. You should see that there's exactly one response that contains this message in the response body. Make a note of the password in the request (the value of `current-password`) to get this response.
6. Login with the credentials `carlos` and the password you just noted. You should be logged in, and lab is solved.
## Payload Used

`username=carlos`
`Referer: url/my-account?id=carlos`
[Candidate password list](../candidatepasswords.txt) (provided by PortSwigger)

Supplying mismatched new passwords ensures the password is never actually changed, avoiding disruption while probing. The `username=carlos` parameter exploits the server's failure to validate that the password change request belongs to the authenticated user.
## Root Cause

The password change functionality implicitly trusts user-controllable content. This, coupled with verbose error messages and the lack of brute force protection, allows us to modify the parameters of a valid request (which we have with `wiener - peter`) to enumerate the login credentials for any arbitrary account, `carlos` in this case.
## Remediation

- Never trust client side controllable data. The app must rely on server-side session data, more specifically, exclusively rely on the session cookie to identify the target user rather than the hidden `username` parameter.
- Implement rate limiting on the password change functionality as with the `/login` endpoint.
- Implement generic error messages  to avoid information disclosure, regardless of whether the current password is correct or the new passwords match.