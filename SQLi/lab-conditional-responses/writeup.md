 ## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: Blind SQL injection with conditional responses](https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses)
- **Date Solved:** 8/4/2026
## Vulnerability Summary

The application is vulnerable to a Boolean-based blind SQL injection in its tracking cookie. The `TrackingId` cookie value is concatenated directly into a backend SQL query without sanitization. An attacker can use this to infer sensitive data, such as administrator credentials, by evaluating true/false conditions based on the presence of the `Welcome back!` message in the HTTP response.
## Reconnaissance

- Injecting the payload `'+AND+'1'='1` (true conditional clause) into the cookie `Cookie: TrackingID = abc` gives us an observable `Welcome back!` message in the response
- However, injecting the payload `+AND+'1'='2` (false conditional clause) gives us nothing. This difference proves that the application is vulnerable to SQLi
## Exploitation Steps

1. Click on any category (e.g. Pets) on the front page of the lab. Intercept this request with Burp Suite proxy interception feature. Send this HTTP Request to Burp Suite Intruder.
2. We need to find out how many characters does the password that belongs to the username `administrator` have. The base payload we're going to use is `'+AND+(SELECT+'a'+FROM+users+WHERE+username='administrator+AND+LENGTH(password)=1)='a`After setting up the payload position to be the number 1 `$1$` and using a list of numbers from 1 to 30 in **Payload configuration**, perform a **Sniper Attack**. Look for a response that differs from everything else in length, as that response is the one that returns `Welcome back!`, signifying the correct length of the password. You'll eventually find out that this number is 20.
3. Now we need to find the actual password. The method I'm going to use is brute forcing. We need to find the correct character for each character in the password, so the amount of requests we normally have to send is roughly `90*20 = 1800` requests! That is an absurd amount of requests, so for this lab, I'm going to use the hint: `You can assume that the password only contains lowercase, alphanumeric characters.` This reduce our search space to just 36 valid choices for each character, making the number of requests sent 720. Injecting this payload after the cookie `'+AND+(SELECT+SUBSTRING(password,1,1)+FROM+users+WHERE+username='administrator')='a` while setting the first payload position to be the **first** `1` and the second payload position to be the character `a` at the end, perform a **Cluster Bomb** attack. The payload list for the second payload position is `a-z` and `0-9`, while the payload list for the first one is trivially `1-20`. Before starting the attack, optionally, you can also configure the **Grep - Match** settings on the side panel to flag responses that match the expression `Welcome back`, as you're looking for correct characters' positions. 
4. Wait for the attack to finish. After it's done, if you configured the `Welcome back` in **Grep - Match** in step 3, the response with `Welcome back` in their body will be automatically put at the top. Otherwise, just sort the length of the response. You'll find exactly 20 responses that have a different length than the rest, because they contain a `Welcome back!` message, which means that the certain character tested is correct in that certain position. Manually construct the full password. 
5. Go on the lab website, type in `administrator` as the username and the password you just constructed. You're now logged in, and lab is now solved!
 
**Notes**
Normally, after the first step, we have to:
1. List the names of all the tables in the database. This is crucial for finding the login credentials for a specific account, as one specific table will contain these information. We need to find the name of this table.
2. After that, we need to list all the column names of that table, in order to the find the names of the ones that contain users' usernames and passwords.
But these information are already given by the lab's description. For what to do in a practical (legal!!!) situation, or when no information is given, refer to [Writeup for lab-listing-database-contents-non-oracle](../lab_listing-database-contents-non-oracle/writeup.md). To confirm that the table `users` exists, inject `'+AND+(SELECT+'a'FROM+users+LIMIT+1)='a`. To confirm that the username `administrator` exists, inject `'+AND+(SELECT+'a'FROM+users+WHERE+username='administrator')='a`. 
## Payload Used

`'+AND+(SELECT+SUBSTRING(password,1,1)+FROM+users+WHERE+username='administrator')='a`
As the known user determining process is done by performing a SQL with the cookie, as long as we have a legit TrackingID (which is obtainable after performing any type of requests), we can append an `AND SELECT` statement to retrieve information by triggering the injected clause and observe whether `Welcome back` (our injected condition is true) appears or not (our injected condition is false). In this case, `SUBSTRING(password,1,1)`is an attempt to find each character of the password (by increasing the first `1`, e.g. `SUBSTRING(password,2,1)`) sequentially, and `'a` is the character being tested.  
## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.
## Remediation

1. Parameterized queries (prepared statement):
```python
query = "SELECT tracking_id FROM tracking_table WHERE tracking_id = ?"
cursor.execute(query, (tracking_id,))
```
2. Strict regex input validation to prevent injection: `^[a-zA-Z0-9]{32}$`.
3. Adopting Principle of Least Privilege (PoLP). User should only have rights to `SELECT` tables they need. 