## Metadata

- **Difficulty:** Apprentice
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: Unprotected admin functionality](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality)
- **Date Solved:** 20/4/2026
## Vulnerability Summary

The app suffers from broken access control, as it does not implement any defense mechanisms for sensitive functionality, allowing for vertical privilege escalation. The administrative URL is disclosed in the website's `robots.txt` file, and this URL is accessible by normal users, granting them sensitive functionalities.
## Reconnaissance

A HTTP `GET` requests to `robots.txt` yields the following response message:
```
User-agent: *
Disallow: /administrator-panel
```
This suggests the existence of a hidden admin panel.
## Exploitation Steps

1. Navigate to `url/robots.txt`. The `Disallowed` field reveals that a very suspicious looking webpage URL that reads `/administrator-panel`.
2. Navigate to `url/administrator-panel`. You should see that there is an option to delete users `carlos` and `wiener`. Delete `carlos`, and the lab is solved.
## Payload Used

`/administrator-panel`.
Sensitive functionalities are granted simply by reaching the admin URL. By finding out the hidden URL through `url/robots.txt`, a normal user or attacker can reach the admin URL and be granted admin's privileges.
## Root Cause

The app does not enforce any protection for sensitive functionality. No authentication or authorization checks or mechanisms are implemented to verify if it's really the intended admin browsing the admin URL or not.
## Remediation

- In the source code of the webapp, declare the access that is allowed for each resource and deny access by default.
- Map users to specific roles, e.g. using RBAC.
- Implement mandatory, server-side access control checks (e.g. through session tokens) on every request to a sensitive endpoint in order to verify the user's role and their privileges. Deny access if there are attempts of privilege escalation.