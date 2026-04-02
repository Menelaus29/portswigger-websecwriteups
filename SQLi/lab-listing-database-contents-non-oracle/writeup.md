## Metadata

- **Difficulty:** Practitioner 
- **Category:** SQL Injection
- **Lab URL:** https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-non-oracle
- **Date Solved:** 2/4/2026
## Vulnerability Summary

The product category filter passes user input directly into a SQL `WHERE` clause of a `SELECT`statement without sanitization. Injecting `UNION SELECT` payloads with `NULL` values allows us to find the number of columns returned by the query. After that, by submitting a series of `UNION SELECT` payloads that place a string value into each column, we can find the column(s) with the ability hold string data. At this stage, we use a `SELECT` statement on `information_schema.tables` to get all the table names in order to identify the table containing users' login credentials, followed by a `SELECT` statement on `information_schema.columns` to find the exact column names of that table. Finally, we can use these column names on the found table containing user login credentials to find the password for the `administrator` account.
## Exploitation Steps

Note: `yourstring` is a random string value initialized by the lab. It differs session to session.
1. Click on any category, e.g. Lifestyle. Intercept this request with Burp Suite intercept function, and send this HTTP request to the Repeater.
2. Find the number of columns returned by the original query (the `WHERE` clause of the `SELECT` statement to filter category) by injecting the `UNION SELECT` payload into the parameter. `'+UNION+SELECT+NULL,NULL--` would return a `200 OK`, indicating that this number is 2.
3. Find the column(s) that accept string data. Injecting the `'+UNION+SELECT+'a','b'--` payload into the parameter would return a `200 OK` HTTP Response, which means both returned columns of the original query accept string data.
4. With these information, we can start finding more about the database. Injecting the payload `'+UNION+SELECT+table_name,NULL+FROM+information_schema.tables--` into the parameter will give us the names of all the tables in the database. The goal of the lab is to login with the username `administrator`, so we need to look for a table with login credentials. That table is named `users_yourstring`(use Ctrl+F after injecting the payload directly on the website's URL to find the `yourstring` part faster). There is only one table with the prefix `users` in this lab.
5. Now that we know the name of the table that contains login credentials, we need to find its columns' names to perform a `SELECT` statement later. Injecting the payload `'+UNION+SELECT+column_name,NULL+FROM+information_schema.columns+where+table_name='users_yourstring'--` will give us the exact names of the columns that contain the usernames and passwords of users: `password_yourstring` and `username_yourstring`.
6. Now that we have the name of the table that (presumably, because we're still not 100% sure at this point) contains the login credentials of all users in the database and its exact column names, finding the password for the username `administrator` is trivial. Inject the payload `'+UNION+SELECT+password_yourstring,username_yourstring+FROM+users_yourstring--` to the parameter, and in the HTTP response, the password for `administrator` is observable (also a random string). 
7. Go on to the website, type in this password along with `administrator` as username. Lab is solved!
## Payload Used

`'+UNION+SELECT+password_yourstring,username_yourstring+FROM+users_yourstring--`
This is just a basic SQL query to return the values in columns named `password_yourstring` and `username_yourstring` in a table named `users_yourstring`. Finding these names is a much more complicated process, as explained in great details in the section **Exploitation Steps**. The `--` comments about the rest of the query, preventing a syntax error.
## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.
## Remediation

See [Writeup for lab-determine-number-of-columns](../lab-determine-number-of-columns/writeup.md).
