## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: Blind SQL injection with conditional errors](https://portswigger.net/web-security/sql-injection/blind/lab-conditional-errors)
- **Date Solved:** 8/4/2026
## Vulnerability Summary

The application is vulnerable to a conditional error blind SQL injection in its tracking cookie. The `TrackingId` cookie value is concatenated directly into a backend SQL query without sanitization. An attacker can use this to infer sensitive data, such as administrator credentials, by evaluating the HTTP response status code `200 OK`/`500 Internal Server Error` to verify the correctness (true/false) of their injected condition.
## Reconnaissance

- Injecting the payload `'`  into the cookie `Cookie: TrackingID = abc` gives us a `500 Internal Server Error` HTTP Response, while `''` gives us a `200 OK`. This confirms that the app is vulnerable to SQLi.
- Injecting the payload `' AND (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE 'a' END)='a` results in a `500 Internal Server Error` HTTP response. This is expected because this query would trigger a division by zero error. However, injecting`' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a` also gives us a `500 Internal Server Error`. This indicates a syntax error.
- Injecting `' AND (SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE NULL END FROM dual)='a` gives us a `200 OK`. This confirms the backend is running Oracle.
## Exploitation Steps

1. Click on any category (e.g. Pets) on the front page of the lab. Intercept this request with Burp Suite proxy interception feature. Send this HTTP Request to Burp Suite Intruder.
2. We need to find out how many characters does the password that belongs to the username `administrator` have. The base payload we're going to use is `' AND (SELECT CASE WHEN (LENGTH(password)=1) THEN TO_CHAR(1/0) ELSE 'a' END FROM users WHERE username='administrator')='a`. After setting up the payload position to be the number 1 `$1$` and using a list of numbers from 1 to 30 in **Payload configuration**, perform a **Sniper Attack**. Look for a response that has the status code `500 Internal Server Error`, signifying that our injected condition for password length testing is true, thus trigger the execution of `TO_CHAR(1/0)`, thus triggers a mathematical error. You'll eventually find out that this number is 20.
3. Now we need to find the actual password. To reduce the search space, I will assume that the password only contains lowercase, alphanumeric characters, just like [Writeup for lab-conditional-responses](../lab-conditional-responses/writeup.md). Injecting this payload after the cookie `' AND (SELECT CASE WHEN (SUBSTR(password,1,1)='a') THEN TO_CHAR(1/0) ELSE 'a' END FROM users WHERE username='administrator')='a` while setting the first payload position to be the **first** `1` and the second payload position to be the character `a` in the comparison clause with `SUBSTR(password,1,1)`, perform a **Cluster Bomb** attack. The payload list for the second payload position is `a-z` and `0-9`, while the payload list for the first one is trivially `1-20`. 
4. Wait for the attack to finish. After it's done, just sort the **status code** of the response in decreasing order. You'll find exactly 20 responses that have a status code of `500 Internal Server Error`, which means that the certain character tested is correct in that certain position. Manually construct the full password. 
5. Go on the lab website, type in `administrator` as the username and the password you just constructed. You're now logged in, and lab is now solved!
 
**Notes**
Normally, after the first step, we have to:
1. List the names of all the tables in the database. This is crucial for finding the login credentials for a specific account, as one specific table will contain these information. We need to find the name of this table.
2. After that, we need to list all the column names of that table, in order to the find the names of the ones that contain users' usernames and passwords.
But these information are already given by the lab's description. For what to do in a practical (legal!!!) situation, or when no information is given, refer to [Writeup for lab-listing-database-contents-oracle](../lab-listing-database-contents-oracle/writeup.md). 
## Payload Used

`' AND (SELECT CASE WHEN (SUBSTR(password,1,1)='a') THEN TO_CHAR(1/0) ELSE 'a' END FROM users WHERE username='administrator')='a`
As the known user determining process is done by performing a SQL query with the cookie, as long as we have a legit TrackingID (which is obtainable after performing any type of requests), we can append an `AND SELECT` statement to retrieve information by triggering the injected clause and observe whether the response is `500 Internal Server Error` (our injected condition is true) appears or `200 OK` (our injected condition is false). In this case, `SUBSTR(password,1,1)`is an attempt to find each character of the password (by increasing the first `1`, e.g. `SUBSTRING(password,2,1)`) sequentially, and `'a'` is the character being tested.  
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
