## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection attack, querying the database type and version on Oracle](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-oracle)
- **Date Solved:** 2/4/2026

## Vulnerability Summary

The product category filter passes user input directly into a SQL `WHERE` clause of a `SELECT`statement without sanitization. Injecting `UNION SELECT` payloads with `NULL` values allows us to find the number of columns returned by the query. After that, by submitting a series of `UNION SELECT` payloads that place a string value into each column, we can find the column(s) with the ability hold string data. With this info, we can extract the `BANNER` column from the `v$version` table, which displays the version number of Oracle Database.
## Reconnaissance

- Testing `'` in the URL parameter throws a `500 Internal Server Error`. User input is being interpreted as SQL query, no sanitization, and this error suggests unhandled SQL syntax error.
- - Testing `+UNION+SELECT+NULL+FROM+DUAL--` throws a `500 Internal Server Error` again. This suggests that the webapp is using Oracle Database, as `DUAL` is a special system table in the Oracle Database system.
## Exploitation Steps

Click on any category on the website (e.g. Gifts) and intercept this request with Burp Suite. Send the request to Burp Suite Repeater. This is where you will be performing the URL parameter payload injecting.
- First, we must find the number of columns returned by the original query. We do this by injecting this payload into the URL parameter: `'+UNION+SELECT+NULL+FROM+DUAL--`, then increasing the number of NULL's until we get a `200 OK` HTTP Response. We would achieve this with 2 `NULL`'s, which means that the original query returns 2 columns. 
- After that, we need to find the column(s) that accept string data. We do this by injecting this payload into the URL parameter: `'+UNION+SELECT+'a',NULL+FROM+DUAL--`. If we get a `200 OK` HTTP Response, that means that the column that we probed with a string value accepts string value. Eventually, we would find that both of these columns accept string data, as `'+UNION+SELECT+'a','b'+FROM+DUAL--` returns `200 OK`.
- With these info, we can inject the payload `+'UNION+SELECT+BANNER,NULL+FROM+v$version--` to find the database type and version. The lab is now solved. This payload can also be directly injected in the website's URL.
## Payload Used

`+'UNION+SELECT+BANNER,NULL+FROM+v$version--` 

`DUAL` is a known existed system table in Oracle Database. For detailed explanation regarding finding the number of columns returned by the original query, see [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md). For detailed explanation regarding finding the column(s) that accept string data, see [Writeup for lab-find-column-containing-text](../lab-find-column-containing-text/writeup.md). `v$version` is a known dynamic performance view in Oracle Database that displays the version number of the database; and in this table, the column `BANNER` holds the component name and version number (see [Oracle Docs](https://docs.oracle.com/en/database/oracle/oracle-database/21/refrn/V-VERSION.html)). If access to this special table were restricted, the payload would not work. 

## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.
## Remediation

See [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md).