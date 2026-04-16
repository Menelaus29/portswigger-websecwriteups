## Metadata

- **Difficulty:** Practitioner
- **Category:** Authentication
- **Lab URL:** [Lab: 2FA broken logic](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic)
- **Date Solved:** 16/4/2026
## Vulnerability Summary

The 2FA verification logic is flawed. After an user has successfully pass the first verification process (with valid login credentials), they are assigned a cookie that relates to their account before being taken to the second verification step (inputting a security code). However, the value of this cookie field can be modified to be of another user to completely bypass the first step of verification, as the app does not verify that the same user is doing the second step. The security code can be bruteforced as there are no implemented rate limiting mechanisms.
## Reconnaissance

- When logging in with our given credentials `wiener` - `peter`, when prompted to type the security code in the URL `url/login2`, if we change the cookie value from `wiener` to `carlos` and hit send, the response has a status code of `200 OK` that is basically identical to the response of the `wiener` value. This suggests that the app never really checked if the first and the second steps of the verification process are done by the same user at all.
## Exploitation Steps

1.  Navigate to `url/login` and log in with the credentials `wiener` - `peter`. You will be taken to `url/login2` where you are prompted to type in a security code. Type a **wrong** one in and intercept this request with Burp Suite proxy. Send the request to the **Repeater** twice. 
2. In the Repeater, on one of the requests, first, change the method from `POST` to `GET`. Second, change the `verify=wiener` to `verify=carlos` (located at the third row from the beginning of the request, same row as `Cookie: session=...`). Finally, delete the `mfa-code=...` at the end. After doing all of that, send the request. This is to prompt the server to generate a legit security code for the account with the username `carlos`. We will be brute forcing this value.
3. On the second request you sent to repeater, change the `verify=wiener` to `verify=carlos` and send the request to **Intruder**. Select the payload position to be the value of the `mfa-code` field, then select the **Payload Type** on the right column to be *Brute forcer*. Set the character set to be `0123456789`, as we are looking for a 4 digit string. The payload and request count should be 10000 (as that's the total number of combinations can be made). Start a **Sniper Attack**, wait for it to finish.
4. After the attack's done, sort the responses' status code in descending order. You should see that there's exactly 1 response that has a status code of `302 Found`, signifying a redirection has taken place, while the rest is `200 OK` with `Incorrect security code` in the response. Right click on the `302 Found` request, and select **Open response in browser**. Copying the URL given then paste on the browser, you should see that you're logged in as `carlos`, and lab is solved.
## Payload Used

- `verify=carlos`
As the app never really checked if the first and the second steps of the verification process are done by the same user at all, modifying the value of the `verify` field after passing the first verification step with username `wiener` completely bypasses the first verification step for the account `carlos`.
## Root Cause

The vulnerability stems from two critical implementation flaws:
1. **Insecure State Management:** The application tracks the intermediate authentication state using a user-controllable client-side mechanism (the `verify` cookie) rather than a secure server-side session. It fails to bind the identity authenticated in step one (username/password) to the identity attempting step two (MFA verification).
2. **Lack of Rate Limiting:** The `/login2` endpoint is completely vulnerable to brute forcing, as it lacks throttling, rate limiting, or account lockout mechanisms. This allows an attacker to exhaust the entire keyspace of the 4-digit security code (10,000 possibilities) without being blocked.
## Remediation

- Client-side data should never be trusted to verify the user identity during MFA. After successful login credentials validation, establish a temporary **server-side** session that maps to the authenticated user (who passed the first step) and marks the state as `pending MFA`.
- Implement defense mechanisms against brute forcing, e.g. account locking after a certain small number (3-5) of wrong security code inputting attempts.
- Expires the MFA token after a short timeframe. 