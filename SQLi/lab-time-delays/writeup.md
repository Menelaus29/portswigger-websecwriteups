## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: Blind SQL injection with time delays](https://portswigger.net/web-security/sql-injection/blind/lab-time-delays)
- **Date Solved:** 14/4/2026
## Vulnerability Summary

The app is vulnerable to SQL injection via its tracking cookie. The `TrackingId` cookie value is concatenated directly into a backend SQL query without sanitization. Though the database errors are caught and handled by the application gracefully, the vulnerability can be confirmed and exploited by injecting database-specific time delay functions.
## Reconnaissance

- Injecting a `'` or a `''` into the cookie `TrackingID` field yields a `200 OK` HTTP Response with no visible verbose database errors nor any differences in the response. This suggests that the vulnerability is blind and non-boolean, thus necessitating a time-delay approach. 
## Exploitation Steps

1. Click on any category under the "Refine your search" to get a legitimate, usable cookie `TrackingID`. Intercept this request with Burp Suite proxy, and send the request to Burp Suite Repeater.
2. Inject the payload `'|| pg_sleep(10)--` into the `TrackingID` field.
3. Observe that the response takes about 10 seconds to arrive. Lab is now solved.
## Payload Used

`'|| pg_sleep(10)--`
To solve this lab, all the information we need is just what kind of database (Oracle, Microsoft, Postgre...) the application is running on. Simply inject different time delay queries for different types of database, you'll eventually arrive at the fact that the underlying database is PostgreSQL.
About the payload, the app must resolve both sides of the concatenation `||` operator before joining them together. Hence, the payload is executed successfully, immediately triggering a time delay of 10 seconds, fulfilling the requirements of the lab.
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