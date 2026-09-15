## Metadata

- **Difficulty:** Practitioner
- **Category:** Business logic vulnerabilities
- **Lab URL:** [Lab: Inconsistent handling of exceptional input](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input)
- **Date Solved:** 15/9/2026
## Vulnerability Summary

The app handles email address lengths inconsistently across different components. The registration endpoint permits arbitrarily long email addresses, but the system truncates the address to exactly 255 characters when processing role-based access control (RBAC). An attacker can exploit this by registering an account with a maliciously crafted, oversized email address that, upon truncation, ends with the privileged `@dontwannacry.com` domain, thereby granting unauthorized administrative access.
## Reconnaissance

- Going to the registration page (`/register`), we see a form with 3 fields: `Username`, `Email`, `Password`. It contains a client-slide note: `"If you work for DontWannaCry, please use your @dontwannacry.com email address"`. Perhaps this email suffix is linked to something?
- Perform a content discovering of the site through Burp (Target > Site map > Right click on the lab's domain > Engagement tools > Discover content > Session is not running). After a while, it discovered an `/admin` endpoint. `DontWannaCry` users do indeed have access to this endpoint, and thus, elevated privileges:
![alt text](<Screenshot 2026-09-15 080038.png>)
- Combined with the hint on the registration page, we probably have to discover a way to register an account with an email that:
	- is (a subdomain of) our provided email in the email client
	- somehow also have the `@dontwannacry.com` suffix when used for role-based access control
Since the lab's name is literally "inconsistent handling", I have decided to go down this path, as in exploiting the `email` parameter. 
- I used Burp Intruder to test different lengths of the email field in the `/register` endpoint. the first payload position, `test$1$`, runs from 1 to 300 with a step of 1. Same with the second payload position, `attacker$1$`.
- The third payload position is placed right after the second payload position. It is configured as character blocks, with a min length of 1 and max length of 300 (300 A's). With a pitchfork attack, 300 requests will be made. All of them returned a `200 OK` HTTP Response with 300 account registration links sent to our email in the email client successfully. This confirms that the `/register` endpoint does not enforce any length validation.
![alt text](<Screenshot 2026-09-15 095043.png>)
- After logging in with accounts registered with abnormal lengths, I noticed that the `Your email is:` field in the `/my-account` is truncated to be exactly 255 characters. For example:
![alt text](<Screenshot 2026-09-15 095321.png>)
Here, the email was 256 characters long, so 1 character at the end (the `t` in `.net`) has been truncated.
![alt text](<Screenshot 2026-09-15 095343.png>)
Here, `ploit-server.net` was truncated, which is exactly the last 16 characters of our 271-character long email.
- The attack path is now clear: we will append the `dontwannacry.com` suffix right after the `@`, then make the email long enough so that everything after that is truncated.
## Exploitation Steps

1. Navigate to the `/register` endpoint.
2. Input normal username (has to be different from every single user name you have registered) and password values, then for the email field, input this:
```
attacker227AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB@dontwannacry.com.exploit-lab-id.exploit-server.net
```
The content of the prefix is not fixed. You should just need to satisfy these 2 conditions:
- The email is exactly 255 characters in length up to the end of the target domain `@dontwannacry.com`. This (normally) results in it being, in total, 315-character long.
- The suffix (string after the `@`) is exactly `dontwannacry.com.exploit-lab-id.exploit-server.net` (substitute your generated `lab-id` in).
Then register the account.
3. Observe that the website shows "Please check your emails for your account registration link". Go to your email client at `/email` and  click on the link associated with the email above. The website should say "Account registration successful!".
4. Log into this account. Observe that your email is truncated to end exactly at the `m` in `dontwannacry.com`, and you know have admin functionalities in the Admin panel.
![alt text](<Screenshot 2026-09-15 095752.png>)
5. Go to the Admin panel and delete user `carlos`. Lab is solved.
## Payload Used

`attacker227AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB@dontwannacry.com.exploit-lab-id.exploit-server.net`
The target truncation length is 255 characters. The privileged suffix `@dontwannacry.com` is 17 characters. Therefore, the prefix (including the username portion) must be exactly 238-character long. When the backend processes this string for RBAC, it drops everything after the 255th character (the `.exploit-lab-id.exploit-server.net` segment), tricking the application into recognizing the user as an administrator.
![alt text](<Screenshot 2026-09-15 095653.png>)
## Root Cause

The vulnerability is caused by inconsistent input validation and data handling across application tiers. The frontend or registration controller accepts inputs exceeding the standard database schema limits, while the backend database strictly enforces a `VARCHAR(255)` constraint (or equivalent). Instead of rejecting the oversized input, the database or ORM silently truncates the data. The RBAC mechanism then evaluates this truncated data rather than the original input, leading to privilege escalation.
## Remediation

- **Application Layer:** The registration endpoint must explicitly validate that the `email` parameter does not exceed the maximum allowable length (255 characters). If the input exceeds this limit, the application must reject the request and return a `400 Bad Request` error.
- **Database Layer:** Ensure the application uses strict SQL modes (e.g., `STRICT_ALL_TABLES` in MySQL) so that data exceeding column lengths results in a database exception rather than silent truncation