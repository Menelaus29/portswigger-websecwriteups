## Metadata

- **Difficulty:** Apprentice
- **Category:** Authentication
- **Lab URL:** [Lab: Username enumeration via different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses)
- **Date Solved:** 15/4/2026
## Vulnerability Summary

The vulnerability is **Information Disclosure via Verbose Error Messages**. Specifically, the app explicitly tells the user (and in this case the attacker) whether an username exists in the database by returning `Invalid username` or `Incorrect password`. This is easily exploitable as the app also fails to rate limit login credentials brute forcing attempts, allowing infinite failed login attempts without defense mechanisms, e.g. account locking, IP blocking. We can simply perform this credentials enumeration using Burp Suite Intruder.
## Reconnaissance

- Typing in random username and password values give us a `Invalid username` response. This suggests that the app's response differs whether the username value exists in the database or not.
## Exploitation Steps

1. Go to `url/login`, and type in random username and password values to send a login request. Intercept this request with Burp Suite proxy and send it to Burp Suite **Intruder**.
2. Set the payload position to be the value of the `username` field. On the **Payload configuration** settings, paste the **candidate usernames** list provided by the lab's description. After doing both of those things, start a **Sniper Attack**. After the attack's done, sort the responses by their length in **descending** order. You should see that there's exactly 1 response that differs from others in length. When you check the details of this response, you should see that it says `Incorrect password` instead of `Invalid username` like all the other responses, suggesting that there's a password for this username that's stored in the database. 
3. Change the value of the `username` field to the the valid username you just got. Now we need to find the password for this username. Just do the same thing as you did before with brute forcing the username: set payload position to be the value of the `password` field, paste the list of **candidate passwords** (also provided by the lab) onto the **Payload configuration** settings, then start a **Sniper Attack**. After the attack's done, sort the responses by their length in **ascending** order. You should see that there's exactly 1 response that is significantly shorter in length from the others. When you check the details of this response, you should see that the status code is `302 Found`, indicating a redirection. Using the obtained username and this password to log in, you should success. Lab is solved!

Notes: A consistent approach to identifying the distinctive responses is to configure the **Grep - Match** settings to flag results containing `Incorrect password` and `302 Found`.
## Root Cause

The app returns verbose error messages for authentication failures based on the validity of the username, leaking sensitive information. Coupled with the lack of rate limiting, the vulnerability is exploitable through brute forcing.
## Remediation

Implement a Defense in Depth (DiD) approach to authentication:
1. **Generic Error Messages:** The application must return identical, generic error messages for all failed login attempts, regardless of whether the username exists or the password is incorrect. Use a unified string `Invalid username or password`.
2. **Account Lockout / Rate Limiting:** Implement strict rate limiting or account lockout mechanisms after a threshold of failed login attempts (e.g., 5 failed attempts within 15 minutes) to neutralize credential stuffing and brute force attacks.
3. **Audit Logging:** Log all failed authentication attempts (without logging the attempted passwords) to monitor for brute-force activity and trigger alerting systems.