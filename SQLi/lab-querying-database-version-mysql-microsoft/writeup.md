## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: SQL injection attack, querying the database type and version on MySQL and Microsoft](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-mysql-microsoft)
- **Date Solved:** 2/4/2026

This is basically [Writeup for lab-querying-database-version-oracle](../lab-querying-database-version-oracle/writeup.md) with syntax differences between Oracle and MySQL. The core workflow is still:
1. Find number of columns returned by original query
2. Find column(s) that accept string data
3. Inject the version function into that column. If there are more than 1 column that accept string data, `SELECT NULL`.
Payload for this lab: `'+UNION+SELECT+@@version,NULL#`

| Oracle     | MySQL/Microsoft        |             |
| ---------- | ---------------------- | ----------- |
| Comment    | `--`                   | `#`         |
| Version    | `v$version` / `banner` | `@@version` |
| Dual table | `FROM dual` required   | Not needed  |
