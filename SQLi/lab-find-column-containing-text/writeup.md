## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection UNION attack, finding a column containing text](https://portswigger.net/web-security/sql-injection/union-attacks/lab-find-column-containing-text)
- **Date Solved:** 2/4/2026

## Vulnerability Summary

The product category filter passes user input directly into a SQL `WHERE` clause of a `SELECT`statement without sanitization. Injecting `UNION SELECT` payloads with `NULL` values allows us to find the number of columns returned by the query. After that, by submitting a series of `UNION SELECT` payloads that place a string value into each column, we can find the column with the ability hold string data, thus making the database retrieve the string assigned to us at random.

## Reconnaissance

Same as [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md)

## Exploitation Steps

First, find the number of columns returned by the original query. See exploitation steps in [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md). It would be 3. After that:
1. Place a string value into each column to test: `' UNION SELECT 'a',NULL,NULL-- `. This would give us a `500 Internal Server Error` -> this not the column we're looking for.
2. Continue placing the string value into each column (**only one column at a time**). Eventually, with the string placed on the middle column, we see a `200 OK` HTTP Response from the server. This is the column that accepts string.
3. Replace the string in that column position with the lab's description string value. Lab is now solved.
## Payload Used

`' UNION SELECT NULL,'your-string',NULL--` 
See the explanation behind `SELECT NULL` and column finding in [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md). In this lab, by probing each column with a string value, we can find the column that accepts string data (not just `NULL`- all columns accept this), thus suitable to inject the specific string value that the lab requires us to do.
## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.
## Remediation

See [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md).

