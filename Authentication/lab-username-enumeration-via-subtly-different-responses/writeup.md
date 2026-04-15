## Metadata

- **Difficulty:** Practitioner 
- **Category:** Authentication
- **Lab URL:** [Lab: Username enumeration via subtly different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses)
- **Date Solved:** 15/4/2026
## Vulnerability Summary

The vulnerability is **Information Disclosure via Verbose Error Messages**. Specifically, the app response differs when a valid username is inputted versus when an invalid one does. Though the difference is hard to spot with the naked eye, using a tool like Burp Suite Intruder makes this much easier. The vulnerability is also easily exploitable as the app also fails to rate limit login credentials brute forcing attempts, allowing infinite failed login attempts without defense mechanisms, e.g. account locking, IP blocking. We can simply perform this credentials enumeration using Burp Suite Intruder.
## Reconnaissance

- Navigate to the `/login` endpoint and submit random input to observe the application's baseline authentication handling. Intercepting this request with Burp Suite proxy, we notice that there's no anti automation token or rate limiting mechanisms -> bruteforce-able.
## Exploitation Steps

1. Go to `url/login`, and type in random username and password values to send a login request. Intercept this request with Burp Suite proxy and send it to Burp Suite **Intruder**.
2. Set the payload position to be the value of the `username` field. On the **Payload configuration** settings, paste the **candidate usernames** list provided by the lab's description. After doing both of those things, start a **Sniper Attack**. After the attack's done, however hard you try, the responses of all the payloads seemingly return `Invalid username or password.`It is almost like there are no differences between valid and invalid usernames. Or is it?
3. On the right side of the screen of the Intruder attack, there's a **Settings** tab. Click on it, scroll down to the **Grep - Extract** section, and click on add. The only possible different between responses is in the `Invalid username of password.` string, so we need to extract this. Click on **Fetch response**, and scroll down to find that message. Highlight it, then click **Ok**.
4. Now run the attack again. You'll notice that this time there's an additional column named `-warning>` with the content being the string we extracted. After the attack's done, sort the responses in ascending order. You'll notice there's exactly one response that very subtly differs from the rest. This is the valid username we're looking for.
5. The job now is easy. Change the value of the `username` field to the the valid username you just got. Now we need to find the password for this username. Set payload position to be the value of the `password` field, paste the list of **candidate passwords** (also provided by the lab) onto the **Payload configuration** settings, then start a **Sniper Attack**. After the attack's done, sort the responses by their length in **ascending** order. You should see that there's exactly 1 response that is significantly shorter in length from the others. When you check the details of this response, you should see that the status code is `302 Found`, indicating a redirection. Using the obtained username and this password to log in, you should success. Lab is solved!
## Payload Used

[Candidate username list](../candidateusernames.txt)
[Candidate password list](../candidatepasswords.txt)
These lists are provided by PortSwigger.
## Root Cause

The app returns verbose error messages for authentication failures based on the validity of the username, leaking sensitive information. Coupled with the lack of rate limiting, the vulnerability is exploitable through brute forcing.
## Remediation

Implement a Defense in Depth (DiD) approach to authentication:
1. **Generic Error Messages:** The application must return identical, generic error messages for all failed login attempts, regardless of whether the username exists or the password is incorrect. Use a unified string `Invalid username or password`.
2. **Account Lockout / Rate Limiting:** Implement strict rate limiting or account lockout mechanisms after a threshold of failed login attempts (e.g., 5 failed attempts within 15 minutes) to neutralize credential stuffing and brute force attacks.
3. **Audit Logging:** Log all failed authentication attempts (without logging the attempted passwords) to monitor for brute-force activity and trigger alerting systems.