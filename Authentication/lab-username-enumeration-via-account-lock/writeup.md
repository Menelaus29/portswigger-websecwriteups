## Metadata

- **Difficulty:** Practitioner 
- **Category:** Authentication
- **Lab URL:** [Lab: Username enumeration via account lock](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-account-lock)
- **Date Solved:** 16/4/2026
## Vulnerability Summary

The application contains a logic flaw in its account lockout mechanism that allows for username enumeration. Specifically, the system only tracks and locks out accounts that actually exist in the database. By intentionally triggering failed logins, an attacker can observe a differential error response `You have made too many incorrect login attempts. Please try again in 1 minute(s).` that confirms a valid username, which can subsequently be brute-forced.
## Reconnaissance

- Submitting random, highly-unlikely-to-exist credentials e.g. `YaeMiko` / `Changli` yields the response `Invalid username or password.` Doing this for 5 more times gives us the same response -> no IP blocking to rate limit brute forcing.
## Exploitation Steps

1. Go to `url/login`, and type in random username and password values to send a login request. Intercept this request with Burp Suite proxy and send it to Burp Suite **Intruder**.
2. Set the payload position to be the value of the `username` field. On the **Payload configuration** settings, paste the **candidate usernames** list provided by the lab's description 5 times (as we need to trigger the flawed account locking mechanism of the app). After doing both of those things, start a **Sniper Attack**. After the attack's done, sort the responses by their length in **descending** order. You should see that there's 5 responses with the same username that differs from others in length. When you check the details of this response, you should see that it says `You have made too many incorrect login attempts. Please try again in 1 minute(s).` instead of `Invalid username of password.` like all the other responses, suggesting that there's a password for this username that's stored in the database. 
3. Wait 1 minute for the account lock to expire.
4. Change the value of the `username` field to the the valid username you just got. Now we need to find the password for this username. Set the payload position to be the value of the `password` field, paste the list of **candidate passwords** onto the **Payload configuration** settings, then start a **Sniper Attack**. After the attack's done, sort the responses by their length in **ascending** order. You should see that there's exactly 1 response that is considerably shorter in length from the others. When you compare the details of the response, you'll notice that this odd-one-out response does not contain the `is warning` class like the others, for example:
```
<p class=is-warning>
You have made too many incorrect login attempts. Please try again in 1 minute(s).</p>
```
Use this password with the username you got from step 2. You should see that you logged in successfully, and lab is solved.
## Payload Used

[Candidate username list](../candidateusernames.txt) x 5 times to hit the lockout threshold for the valid user.
[Candidate password list](../candidatepasswords.txt)
These lists are provided by PortSwigger.
## Root Cause

The business logic applies the account lockout security control conditionally based on account existence, thus fails to implement a uniform response. The application leaks the internal state of the database by confirming that a specific account has reached a failed-attempt threshold, a state impossible to reach for invalid usernames.
## Remediation

- Return a uniform response for all failed authentication attempts, regardless of whether the account exists or is locked, e.g. `Invalid credentials or account is locked`.
- Implement rate limiting mechanism based on IP address or device fingerprinting rather than solely on the username.
