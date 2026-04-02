## Metadata

- **Difficulty:** Apprentice
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection vulnerability in WHERE clause allowing retrieval of hidden data | Web Security Academy](https://portswigger.net/web-security/sql-injection/lab-retrieve-hidden-data)
- **Date Solved:** 1/4/2026
## Vulnerability Summary

The product category filter passes user input directly into a SQL `WHERE` clause without sanitization. Injecting into the `category` parameter in the URL allows us to rewrite the query logic and retrieve rows the application intends to hide (with `AND released = 1` in this case).
## Reconnaissance

- Clicking any category, e.g. Accessories, produces this request: `GET /filter?category=Accessories` and takes us to the URL where items are filtered by `filter?category=Accessories` . The webapp is likely filtering a database table by category. This filtering mechanism shows/hides products depends on the category selected.
- Testing `'` in the URL parameter throws a `500 Internal Server Error`. User input is being interpreted as SQL query, no sanitization, and this error suggests unhandled SQL syntax error.
## Exploitation Steps

With Burp Suite:
1. Intercept the request (when clicked on the Accessories section, `GET /filter?category=Accessories` ) with Burp Suite. 
2. Modify the parameter: `GET /filter?category=Accessories'OR+1=1--`
3. The HTTP response sent from the server indicates that the lab is solved.

We can also inject the payload directly to the URL:
`https://...web-security-academy.net/filter?category=Accessories'OR+1=1--`
The webapp now shows all the items, including the hidden/unreleased ones.
## Payload Used

`' OR+1=1--` (`+` is the encoded space character).
`OR 1=1` forces every row to match (because it's always TRUE), while `--` comments out the remainder of the query, eliminating the `AND released = 1` gate entirely. This results in the return of all products regardless of their released/unreleased status.
## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.
## Remediation

Using parameterized queries (prepared statement). The query can be structured as:
````python
cursor.execute(
	"SELECT * FROM product WHERE category = ? AND RELEASED = 1",
	(category,)
)
````
User input is treated only as data passed to the SQL query, not the query itself.
