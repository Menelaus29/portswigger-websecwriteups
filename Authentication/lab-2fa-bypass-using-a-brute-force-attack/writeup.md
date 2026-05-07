## Metadata

- **Difficulty:** Expert
- **Category:** Authentication
- **Lab URL:** [Lab: 2FA bypass using a brute-force attack](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack)
- **Date Solved:** 7/5/2026
## Vulnerability Summary

The only defense mechanism implemented to prevent the brute forcing of 2FA verification code is that the app logs us out after 2 incorrect 2FA attempts, thus, we need to reauthenticate (`GET /login -> POST /login -> GET /login2`) to get a fresh session cookie and CSRF token. However, this reauthentication process can be automated, rendering this mechanism bypassable and bruteforcing still valid.
## Reconnaissance

- After navigating to `url/login` and logging in with credentials `carlos - montoya`, we are prompted with inputting the 2FA code. We see that after 2 wrong attempts, the app logs us out and we have to log in again. But after logging in again, I notice that we can try 2 more times before being logged out, just like before. Thus, an automation script of some kind is adequate to bypass this defense mechanism.
## Exploitation Steps

I have no idea how to perform this kind of automation with Caido at the moment. This section will be updated when I figure it out. Please open an issue if you know how to, it will be greatly appreciated. 
As of now, refer to the [Python automation script](exploit.py). Cookies is clear with `session.cookies.clear()` every iteration to ensure that a new pair of session cookie and CSRF token is generated every run, bypassing the defense mechanism. The workflow:
- Obtains a new CSRF token with a `GET` HTTP request to the `/login` endpoint.
- Logs in with a `POST` HTTP request, using the obtained CSRF token and the credentials `carlos - montoya`.
- Obtains a CSRF token with a `GET` HTTP request to the `/login2` endpoint.
- Try a 4 digit 0 padded number for the 2FA code. If the HTTP response for this request has a status code of `302 Found`, signifying a redirection, the script prints out the valid 2FA code, the session cookie, and automatically makes a `GET` HTTP request to confirm lab is solved.
The script is run concurrently on multiple threads (configurable with parameter `--threads`) to speed up the brute force process. Each thread gets an independent slice of the 0000-9999 range and its own `requests.Session` to avoid problems with shared state. A `threading.Event` stops all threads the moment any one of them finds the code.
## Payload Used

Brute force list: 0 padded 4 digit numbers from 0000 to 9999.
[Python automation script](exploit.py).
## Root Cause

The app's bruteforce protection is flawed. Logging an user out if they enter a certain number of incorrect verification codes (in this case, 2) is ineffective as we can automate the reauthentication process, completely bypassing this defense mechanism.
## Remediation

- Implement account based rate limiting. Instead of tracking the failed 2FA verification attempts against the session cookie, do it against the user's identity.
- Implement a temporary account lockout mechanism server-side after a certain number of failed 2FA verification attempts.