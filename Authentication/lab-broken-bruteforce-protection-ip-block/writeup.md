## Metadata

- **Difficulty:** Practitioner
- **Category:** Authentication
- **Lab URL:** [Lab: Broken brute-force protection, IP block](https://portswigger.net/web-security/authentication/password-based/lab-broken-bruteforce-protection-ip-block)
- **Date Solved:** 16/4/2026
## Vulnerability Summary

The app tracks failed login attempts by IP address, but completely clears the failed-attempt counter for that IP upon _any_ successful login, regardless of which account was successfully accessed. Coupled with the verbose error messages where the app explicitly tells the user (and in this case the attacker) whether an username exists in the database by returning `Invalid username` or `Incorrect password`, the password for the username is exploitable through brute forcing.
## Reconnaissance

- Typing in random username and password values give us a `Invalid username` responses, while valid usernames like `carlos` and `wiener` yields `Incorrect password` ones.
- The app blocks us from trying to log in after 3 failed attempts, but after a successful one (with `wiener` - `peter`, the same number of failed attempts can be done. This suggests that this counter is reset in the event of a successful login attempts.
## Exploitation Steps

First, we need to create 2 lists of alternatingly password guessing attempts and successful login attempts from our given credentials. Since the block triggers after 3 failed attempts, a 1:1 alternating ratio is safe. Therefore, each list has 200 entries (because the original candidate password list has 100 entries). You can find the lists here: [Integrated username list](integratedusernames.txt), [Integrated password list](integratedpasswords.txt). Now:

1. Go to `url/login`, and type in random username and password values to send a login request. Intercept this request with Burp Suite proxy and send it to Burp Suite **Intruder**.
2. Set the first payload position to be the value of the `username` field. On the **Payload configuration** settings, paste the **Integrated username list**. After that, select the second payload position to be the value of the `password` field, and paste the **Integrated password list** onto its payload list. Then, start a **Pitchfork Attack** in Burp Suite Intruder. After the attack's done, sort the **Status code** column in descending order - as we are looking for `302 Found` which signifies a redirection instead of a `200 OK`. Amidst the successful login attempts for the username `wiener`, there is one successful one for the username `carlos`. The password used in that response is what we are looking for. 
3. After obtaining the password, go on the website and type in the login credentials: `carlos` as username and whatever you just got as password. You should see that you're logged in as `carlos`. Lab is solved!
## Payload Used

[Integrated username list](integratedusernames.txt)
[Integrated password list](integratedpasswords.txt) 
## Root Cause

The app returns verbose error messages for authentication failures based on the validity of the username, leaking sensitive information. Coupled with the flawed brute force protection, the vulnerability is exploitable through alternating between password brute forcing and successful login attempts.
## Remediation

Address both the flawed business logic in the rate-limiting mechanism and the information disclosure vulnerability:
* **Correct Rate Limit Reset Logic:** Isolate the failed authentication counter resets. A successful login must *only* reset the failure counter for that specific authenticated account. It must never clear the global IP-based failure counter or the counters for other accounts targeted by the same IP.
* **Implement Granular Tracking:** Track and limit failed authentication attempts using a combination of both the IP address and the Username independently. This prevents attackers from bypassing IP blocks by rotating IPs (credential stuffing) or bypassing account locks by rotating targeted users (password spraying).
* **Unify Error Messages:** Return a generic, identical error message (e.g., "Invalid username or password") and consistent response times/status codes for all failed login attempts, regardless of whether the username exists in the database.