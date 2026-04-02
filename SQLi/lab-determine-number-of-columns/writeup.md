## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection UNION attack, determining the number of columns returned by the query](https://portswigger.net/web-security/sql-injection/union-attacks/lab-determine-number-of-columns)
- **Date Solved:** 2/4/2026

## Vulnerability Summary

The product category filter passes user input directly into a SQL `WHERE` clause of a `SELECT`statement without sanitization. Injecting `UNION SELECT` payloads with `NULL` values allows us to find the number of columns returned by the query.
## Reconnaissance

- Testing `'` in the URL parameter throws a `500 Internal Server Error`. User input is being interpreted as SQL query, no sanitization. 

## Exploitation Steps

1. Click on any category (e.g. Gifts), intercept that request with Burp Suite.
2. Inject `'+UNION+SELECT+NULL--` into the parameter in Burp's Repeater. This would give us a `500 Internal Server Error`
3. Continue adding `NULL` values. Eventually, with the payload 
`'+UNION+SELECT+NULL,NULL,NULL--` , the server returns a `200 OK`. Lab is solved.

## Payload Used

`'+UNION+SELECT+NULL,NULL,NULL--` (+ is the URL-encoded space (`' '`) character)

`SELECT NULL`, as a standalone query, returns a single row with a single column containing `NULL`. Each additional `NULL` increases the column count of the injected query by one. Also, since `NULL` is compatible with any data type and `UNION` requires the individual queries to return the same number of columns, we can use these info to sequentially increase the number of `NULL`'s in our payload until the server stops returning an error (because of different column numbers between the original query and our injected payload) in its HTTP response. When the server stops returning an error, the number of `NULL`'s in our payload is the number of columns returned in the original query.
## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.

## Remediation

1. Parameterized queries (prepared statement):
```python
query = "SELECT * FROM products WHERE category = %s"
cursor.execute(query, (category,))
```
2. Allowlist input validation (so that NULL is incompatible):
```python
VALID_CATEGORIES = {"Accessories", "Clothing, shoes and accessories", "Food & Drink", "Lifestyle", "Pets"}
if category not in VALID_CATEGORIES:
    return 400  # Reject unknown input
```
3. Adopting Principle of Least Privilege (PoLP). User should only have rights to `SELECT` tables they need. 