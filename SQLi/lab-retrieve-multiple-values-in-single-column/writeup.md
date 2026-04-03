`'+UNION+SELECT+NULL,NULL--`
`'+UNION+SELECT+NULL,'b'--`
`'+UNION+SELECT+NULL,username||'~'||password+FROM+users--`
## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection UNION attack, retrieving multiple values in a single column](https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-multiple-values-in-single-column)
- **Date Solved:** 3/4/2026

Basically the same as [Writeup for lab-listing-database-contents-non-oracle](../lab-listing-database-contents-non-oracle/writeup.md), even much simpler since the name of the table that contains login credentials and its exact column names are already given by the lab's description. We only need to:
1. Find the number of columns returned by the original query, with 
 `'+UNION+SELECT+NULL,NULL--`.
2. Find the column(s) that accept string data. The goal of this lab is too retrieve multiple values in a single column, so intuitively only 1 column out of the 2 returned accepts string data. `'+UNION+SELECT+NULL,'b'--` gives a `200 OK` HTTP response, signifying that the second column is the one to do the information lookup.
3. We need to have both the username and password returned in this single column. To do this, we simply concatenate the values together and separate them with a special character to distinguish between the username and the password. Inject the payload `'+UNION+SELECT+NULL,username||'~'||password+FROM+users--` into the parameter, and you shall find a string that reads `administrator-randomstring`. Go on the website, input `administrator` as username and that `randomstring` as password, and you will find that the lab is solved.