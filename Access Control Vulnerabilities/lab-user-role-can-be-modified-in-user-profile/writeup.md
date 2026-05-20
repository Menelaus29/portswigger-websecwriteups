## Metadata

- **Difficulty:** Apprentice
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: User role can be modified in user profile](https://portswigger.net/web-security/access-control/lab-user-role-can-be-modified-in-user-profile)
- **Date Solved:** 20/5/2026
## Vulnerability Summary

The app determine the user's role (access rights) by checking a field in a user controllable location. This allows for vertical privilege escalation through a simple modification.
## Reconnaissance

- Navigating to `url/admin` before logging in, we get a `401 Unauthorized` HTTP response that reads "Admin interface only available if logged in as an administrator". There's no modifiable field in the request that might bypass this check.
- Logging in with the credentials `wiener - peter` and trying to change the email (e.g., to `wiener1@normal-user.net`) will result in a `302 Found` HTTP Response that reads:
```
{
    "username": "wiener",
    "email": "wiener1@normal-user.net",
    "apikey": "uLuAdq2mFVdN4xWk2teLE59v0k0METVD",
    "roleid": 1
}
```
This suggests that role and access rights are checked by using the `roleid` field. Per the lab description, we know that a `roleid` of 2 will have administrative functionalities. We can try to modify this `roleid` by appending the field into our request.
## Exploitation Steps

1. Log in with the credentials `wiener - peter` (given by the lab).
2. After logging in, on `url/my-account`, change your email to any value, e.g. `wiener1@normal-user.net`. Intercept this request.
3. On the intercepted request, add the `roleid: "2"` line to the JSON block inside the request body. Your modified request should look something like the block below. Send the request.
```
POST /my-account/change-email HTTP/1.1

...

{
  "email":"wiener1@normal-user.net",
  "roleid": 2
}
```
4. Observe that you received a `302 Found HTTP Request` that contains this `JSON` block:
```
{
    "username": "wiener",
    "email": "wiener1@normal-user.net",
    "apikey": "randomstring",
    "roleid": 2
}
```
5. Refresh the `url/my-account` page. You should see that you have a clickable admin panel button on the upper right of the website, below the header. Click on that (or go to `url/admin`), and you should see that there's an option to delete users `wiener` and/or `carlos`. Delete `carlos`, and lab is solved.
## Payload Used

```
{
  "email":"wiener1@normal-user.net",
  "roleid": 2
}
```
Appending the `"roleid": 2` grants us administrative rights.
## Root Cause

The app suffers from a Broken Access Control vulnerability. The server trusts user-submitted data for access control decisions, which allows users to vertically escalate their privilege level by tampering with the `roleid` parameter during a profile update. Technically, this is known as *Mass Assignment*, where the backend binds the client-provided JSON payload directly to the internal user object without filtering out unchangeable fields.
## Remediation

Do not rely on modifiable request parameters for access control decisions. All access control decisions should be based on verified, immutable user context on the server. To prevent Mass Assignment specifically, implement strict allow-lists for user-controllable inputs. Use Data Transfer Objects (DTOs) or framework-specific configurations to explicitly ignore sensitive fields (like `roleid`) during database record updates.