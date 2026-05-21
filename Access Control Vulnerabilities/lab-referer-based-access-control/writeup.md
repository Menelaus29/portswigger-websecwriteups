## Metadata

- **Difficulty:** Practitioner 
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: Referer-based access control](https://portswigger.net/web-security/access-control/lab-referer-based-access-control)
- **Date Solved:** 21/5/2026
## Vulnerability Summary

The app is vulnerable to Broken Access Control. It controls the role upgrading/downgrading function based on the user-controllable `Referer` header, and blindly trusts it for access control checks. We can exploit this by modifying the value of this header to perform vertical privilege escalation.
## Reconnaissance

Navigate to `url/login` and log in with credentials `administrator - admin`. Intercept the request to upgrade the role of user `carlos` (from `NORMAL` to `ADMIN`). We notice that the value of the `Referer` header is `url/admin`. Now log out, then log in to `wiener`'s account (`wiener - peter`). Try to perform the same upgrade request from `wiener`'s account - you will get a `401 Unauthorized` HTTP Response. Exact same request but with the header `Referer: https://<lab-id>.web-security-academy.net/admin` yields a `302 Found` HTTP Response with header `Location: /admin`. This suggests that the app only perform access control checks by inspecting the `Referer` header.
## Exploitation Steps

1. Log in to `wiener`'s account with credentials `wiener - peter`.
2. Intercept the `GET` request to go to `/my-account?id=wiener` after logging in.
3. Change the header of the intercepted `GET` request to `GET /admin-roles?username=wiener&action=upgrade HTTP/1.1`. Add the `Referer` header in the request: `Referer: https://<lab-id>.web-security-academy.net/admin`.
4. Send the request. You should get a `302 Found` HTTP Response with `Location: /admin`. Go on the website, and you should see that lab is solved.
## Payload Used

`Referer: https://<lab-id>.web-security-academy.net/admin`
The app only checks the value of the `Referer` header for the role upgrade/downgrade functionality. Thus, as long as we have this header, we can upgrade/downgrade the role of any arbitrary user.
## Root Cause

The app bases access controls on the `Referer` header. It insecurely and implicitly trusts this user-controllable header to enforce access control. Thus, we can modify and supply the required `Referer` header to forge direct requests to sensitive pages and gain unauthorized access. 
## Remediation

Never rely on user-controllable data—such as the `Referer` header, `User-Agent`, hidden fields, or unencrypted cookies—to enforce access control decisions. The application must implement robust Role-Based Access Control (RBAC) on the server side. Evaluate user privileges dynamically per-request against a trusted backend session object, ensuring the authenticated user mapped to the active session identifier explicitly holds the administrative role required to access the sensitive, restricted endpoints.