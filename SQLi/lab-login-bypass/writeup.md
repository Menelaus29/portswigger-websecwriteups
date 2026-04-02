## Metadata

- **Difficulty:** Apprentice
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection vulnerability allowing login bypass](https://portswigger.net/web-security/sql-injection/lab-login-bypass)
- **Date Solved:** 1/4/2026
## Vulnerability Summary

The login parameters inputting screen passes user input to check login credentials by performing a SQL query. Injecting a common username, e.g. `admin` or `administrator` with the SQL comment sequence `--` allows us to bypass the password check, logging us in as the user with the username.
## Reconnaissance

- Testing `'` in the URL parameter throws a `500 Internal Server Error`. User input is being interpreted as SQL query, no sanitization, and this error suggests unhandled SQL syntax error.
## Exploitation Steps

With Burp Suite:
1. Fill in the login parameters fields with random value and Intercept the login request with Burp Suite. 
2. Modify the username parameter: `csrf=[your csrf]&username=administrator'--&password=[any random value]`.
3.  The HTTP response to this request should have a status code of `302 Found`, indicating a redirect occurred. The location should be `/my-account?id=administrator`, which is the administrator's account page. A new cookie session should also be observable, which means that a valid authenticated sessions was created.

We can also inject the payload (`administrator'--)` directly to the username field of the login page to get the same results.
## Payload Used

`administrator'--` (and a random string as password). This would work with any valid username, not just `administrator`. 
- The app checks the login credentials by performing a SQL query, e.g.
``SELECT * FROM users WHERE username = 'wiener' AND password = 'bluecheese'``
- When we inject the payload above and a random password, the app performs this SQL query:
 ``SELECT * FROM users WHERE username = 'administrator'--' AND password = 'sdfdsf'``
 - The `--` comments out the rest of the query, bypassing everything after the username check, including the password check.
## Root Cause
User-controlled input is concatenated into a SQL query with no escaping or parameterization.

## Remediation
Using parameterized queries (prepared statements). The query can be structured as:
````python
cursor.execute(
	"SELECT * FROM users WHERE username = ? AND password = ?,
	(username, password)
)
````
User input is treated only as data passed to the SQL query, not the query itself.