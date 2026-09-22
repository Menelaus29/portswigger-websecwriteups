## Metadata

- **Difficulty:** Apprentice
- **Category:** Information disclosure
- **Lab URL:** [Lab: Source code disclosure via backup files](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-via-backup-files)
- **Date Solved:** 22/9/2026
## Vulnerability Summary

The app is vulnerable to information disclosure. Its `/robots.txt` file exposes an accessible `/backup` endpoint containing a `.bak` backup file (`ProductTemplate.java.bak`). This file leaks sensitive database connection credentials, including the plaintext database password, directly within a `ConnectionBuilder.from()` method call, enabling unauthorized infrastructure access.
## Reconnaissance

- The app is a simple online shop webapp. You can navigate to an item with the request `GET /product?productId=x`, with `x` being a number. Navigating to common endpoints like `/robots.txt`reveals the `/backup` endpoint:
```
User-agent: *
Disallow: /backup
```
- Visiting this endpoint reveals a directory listing containing a backup file, `ProductTemplate.java.bak`. We are able to read this file. It imports a class based on Java's `ConnectionBuilder` interface. Then, it wraps database connection parameters (driver, protocol, host, port, user, password) into a builder object to open SQL connections:
```java
private void readObject(ObjectInputStream inputStream) throws IOException, ClassNotFoundException
    {
        inputStream.defaultReadObject();
        ConnectionBuilder connectionBuilder = ConnectionBuilder.from(
                "org.postgresql.Driver",
                "postgresql",
                "localhost",
                5432,
                "postgres",
                "postgres",
                "[password-string]"
        ).withAutoCommit();
```
Thing is, the values of these parameters are all hardcoded, leaking sensitive information, which in this case, the PostgreSQL database password.
## Exploitation Steps

1. Navigate to the `/robots.txt` endpoint to discover disallowed paths, identifying the `/backup` directory.
2. Navigate to the endpoint `/backup`. You should receive a `200 OK` HTTP response displaying a directory listing containing `ProductTemplate.java.bak`.
3. Access `ProductTemplate.java.bak`. Observe that the hardcoded database password is passed as a parameter in the method `ConnectionBuilder.from()`:
```java
        ConnectionBuilder connectionBuilder = ConnectionBuilder.from(
                "org.postgresql.Driver",
                "postgresql",
                "localhost",
                5432,
                "postgres",
                "postgres",
                "[password-string]"
        ).withAutoCommit();
```
3. Extract the `[password-string]` and submit it (`POST /submitSolution`). Lab is solved.
## Payload Used

```
GET /backup/ProductTemplate.java.bak HTTP/1.1
```

Compiled Java applications normally execute server-side within a servlet container, serving only compiled execution results or rendered HTML to clients. However, web servers route and execute files based on file extensions. When non-executable extensions such as `.bak`, `.old`, or `~` are placed inside a web-accessible directory, the server fails to route them to the execution engine. Instead, it falls back to serving the file as raw static text (`text/html` in this case), exposing the underlying uncompiled source code and hardcoded secrets directly.
## Root Cause

- Deployment or developer backup artifacts (`.bak` files) were stored in the public web root directory, and the path was exposed via `/robots.txt`. The web server was not configured to block access to non-standard or backup file extensions.
- Production database connection parameters and credentials were hardcoded directly within app source code rather than being retrieved dynamically at runtime from environment variables/dedicated secrets manager.
## Remediation

- Exclude source files, editor swap files, version control metadata (`.git`), and `.bak` archives from web-accessible directories in CI/CD pipelines.
- Configure the web server or reverse proxy to deny requests to backup, temporary, and hidden file extensions:
```nginx
location ~* \.(bak|old|orig|save|tmp|swp)$ {
    deny all;
    return 404;
}
```
- Store database credentials outside the codebase using environment variables or a secrets management service.
- Do not rely on `/robots.txt` to protect sensitive directories. Combined with removing sensitive paths from this file, restrict access using proper authorization and web server access controls.
