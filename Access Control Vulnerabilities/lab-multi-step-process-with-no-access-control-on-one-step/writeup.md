## Metadata

- **Difficulty:** Practitioner
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: Multi-step process with no access control on one step](https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control-on-one-step)
- **Date Solved:** 21/5/2026
## Vulnerability Summary

The app is vulnerable to Broken Access Control. There are 2 steps to upgrading/downgrading an user's role, however access controls are only implemented in the first step, not on the second one (which is confirming the upgrading/downgrading). We can exploit this by skipping the first step and directly submitting the request for the second step to promote ourselves, vertically escalating our privileges. 
## Reconnaissance

Navigate to `url/login` and log in with credentials `administrator - admin`. Intercept the 2 requests in the process of upgrading `carlos`'s role - the action of upgrading itself and the confirmation screen for it. Now logged out of the `administrator`'s account, and log in to `wiener`'s one (`wiener - peter)`. Replacing `administrator`'s session cookie with `wiener`'s session cookie in the 2 requests and send them, we see that the request for the first step returns a `401 Unauthorized`, while on the second step we get a `302 Found` with a HTTP header `Location: /admin`. This confirms that the app only implements access controls check for the first step and not the second one.
## Exploitation Steps

1. Navigate to `url/login` and login with credentials `administrator - admin`.
2. Intercept the request to confirm the upgrade of an user (the second step in the upgrading process). 
3. Log out, and log in to `wiener`'s account with credentials `wiener - peter`.
4. Intercept the request to go to `/my-account?id=wiener` after logging in to get `wiener`'s session cookie.
5. Using this session cookie, replace the `administrator`'s session cookie in the intercepted request in step 2. In the same request, modify the `username` parameter in the last line to `wiener`: `action=upgrade&confirmed=true&username=wiener`. 
6. Send the request. You should get a `302 Found` HTTP Response with `Location: /admin`. Go on the website, and you should see that lab is solved.
## Payload Used

`username=wiener`
Since the app does not implement access control checks in step 2 of the upgrading process, as long as we have the request template for this step, any user can upgrade/downgrade the role of any arbitrary user.
## Root Cause

The role upgrading/downgrading process is in multiple steps, but the app does not implement adequate access control checks for all of these steps. Thus, we can bypass the checks of the previous step by skipping the first step and directly submitting the request for the second one with the required parameters. 
## Remediation

Access control validation must be enforced on the server-side at every single step of a multi-step process, especially on the final one where the state-changing action is executed. Do not rely on users following the intended sequence of steps. Before applying the role upgrade in the database, the application must explicitly verify that the user associated with the current session token holds the necessary administrative privileges.