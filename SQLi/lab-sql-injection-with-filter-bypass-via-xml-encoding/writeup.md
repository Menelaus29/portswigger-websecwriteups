## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection with filter bypass via XML encoding](https://portswigger.net/web-security/sql-injection/lab-sql-injection-with-filter-bypass-via-xml-encoding)
- **Date Solved:** 15/4/2026
  
## Vulnerability Summary

The app is vulnerable to SQL injection via its `<productId>` and `storeId`. Though there are defense mechanisms, presumably via a WAF, that blocks certain SQLi keywords, these filters are weak and can be bypassed by encoding characters in the prohibited keywords, using Burp Suite extension **Hackvertor**. The bypass works because, firstly, the WAF inspects the raw, encoded XML, sees nothing malicious and passes it to the backend. The backend XML parser decodes the entities before passing the payload to the vulnerable SQL query
## Reconnaissance

- Putting `1+1` in the `<productId>` and `<storeId>` fields has the same effect as `2`. This suggests that the mathematical expression `1+1` is being executed by the app, confirming vulnerability to SQLi.
## Exploitation Steps

1. Click on the **View details** option of any random product. At the end of the product's description, there is a **Check stock** option. Choose a random city and click on it. Intercept this `POST /product /stock` request Burp Suite proxy and send it to the **Repeater**.
2. We need to determine the number of columns returned by the original query. For more details on how this works, see [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md). For this lab, encoding the base payload `2 UNION SELECT NULL--` with **Hackvertor**'s encode -> `hex_entities` and then injecting the encoded payload (below) to the `<productId>` field gives us the application's intended results and a `null` value in the response, confirming that the original query returns 1 column.
```
<@hex_entities>
2 UNION SELECT NULL--
</@hex_entities>
```
3. We need to return both the usernames and passwords on this one column. To do this, we inject the payload below into the `<productId>` field. You shall find  a string that reads `administrator~randomstring`. Go on the website, input `administrator` as username and that `randomstring` as password, and you will find that the lab is solved.
```
<@hex_entities>
2 UNION SELECT username || '~' || password FROM users--
</@hex_entities>
```
## Payload Used

```
<@hex_entities>
2 UNION SELECT username || '~' || password FROM users--
</@hex_entities>
```
The query itself is just a simple `SELECT` statement that concatenates the values together to return them on a single column in order to fulfill the requirements of 1 column returned by the original query. The `<@hex_entities>` encoding bypass the weak filters of WAF to make the app executes this query.
## Root Cause

- The application extracts values from the `<productId>` or `<storeId>` nodes of the parsed XML document and directly concatenates them into a backend SQL query without adequate sanitization or parameterization, allowing SQLi
- The application relies on a Web Application Firewall (WAF) or an input filter to detect SQLi keywords (like `UNION` or `SELECT`). However, the WAF evaluates the raw HTTP request body without fully normalizing XML entities. Because the payload is injected using XML hex entities, the WAF fails to recognize the signatures and allows the request. The backend application's XML parser then legitimately decodes these entities into literal strings _before_ executing the unsafe database query, successfully delivering the payload
## Remediation

- **Implement Parameterized Queries (Prepared Statements):** This is the primary and most effective fix. Ensure that the database driver uses parameterized queries for all database interactions. By strictly binding the parsed XML values as data parameters rather than executable SQL syntax, the database will treat the input safely, regardless of any encoded characters or keywords it contains.
- **Normalize Input at the WAF (Defense in Depth):** Configure the WAF or security filter to perform protocol-level and payload-level normalization prior to signature matching. The WAF must fully decode XML entities, URL encoding, and Unicode escapes before evaluating the data against its SQLi rule set.
- **Strict Input Validation (Whitelisting):** Since `productId` and `storeId` should logically be integers, enforce strict server-side type checking and validation. If the extracted value is not a valid integer, the application should reject the request before it ever reaches the database layer.