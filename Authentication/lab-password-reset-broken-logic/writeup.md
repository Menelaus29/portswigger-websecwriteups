## Metadata

- **Difficulty:** Apprentice
- **Category:** Authentication
- **Lab URL:** [Lab: Password reset broken logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic)
- **Date Solved:** 29/4/2026
## Vulnerability Summary

The app's password reset functionality is vulnerable. Specifically, the app fails to validate the temporary password reset token when the reset form is submitted, thus allowing us to delete this token entirely to reset the password of any arbitrary user.
## Reconnaissance

After navigating to `url/login` and click on "Forgot password?", we'll be taken to `url/forgot-password` and be prompted to type in your username. Type in `wiener`, click "Submit", then check your email (click on the "Email client" button on the lab's header) for the recovery link. Following the link for password reset, we are taken to `url/forgot-password?temp-forgot-password-token=randomstring`(`random string` is a value that differs from session to session). Type in 2 identical random strings, then intercept the request before clicking the "Submit" button. The intercepted request body should have a HTTP header of `POST /forgot-password?temp-forgot-password-token=randomstring` and a body that read `temp-forgot-password-token=randomstring&username=wiener&new-password-1=randompassword&new-password-2=randompassword`. Deleting the value of the field `temp-forgot-password-token` in both the header and the body, we are able to bypass the token check completely thus reset the password of our account without ever needing the value of  this token. This suggests that the app does not validate the temporary password reset token when the reset form is submitted.  
## Exploitation Steps

1. Navigate to `url/login` and click on "Forgot password?". You'll be taken to `url/forgot-password` and be prompted to type in your username. Type in `wiener` then click "Submit".
2. Click on the "Email client" button on the lab's header for the recovery link. Follow this link, where you are prompted to type in and confirm your new password. Type in anything, e.g. "a". Intercept this request before you click "Submit".
3. On the intercepted request, delete the value of the `temp-forgot-password-token` in the HTTP header **and** the body. Change the username to `carlos`. Your request should look like the block below. Send the request.
```
POST /forgot-password?temp-forgot-password-token= HTTP/1.1

...

temp-forgot-password-token=&username=carlos&new-password-1=a&new-password-2=a
```
4. Observe that the response has a status code of `302 Found`, signifying a redirection. Go on the website, type in the username `carlos` and the value of the password of the request you just sent (in my case, "a"), and you should see that you have successfully logged in as `carlos`. Lab is solved!
## Payload Used

`POST /forgot-password?temp-forgot-password-token= HTTP/1.1`
`temp-forgot-password-token=&username=carlos&new-password-1=a&new-password-2=a`

Since the app does not check the the temporary password reset token when the reset form is submitted, deleting this value from the request bypasses the need for its existence completely.
## Root Cause

When an user visits a password recovery link, the system correctly checks if the token exists on the back-end in order to validate a legitimate password reset request. However, it fails to also validate the token again when the reset form is submitted. Thus, we can simply visit the reset form from our own account `wiener`, delete the token, and leverage this page to reset an arbitrary user's password, which, in this case, `carlos`.
## Remediation

- The app must require and validate the `temp-forgot-password-token` during the `POST /forgot-password` request
- The app must not rely on and trust user-controllable output like the hidden `username` field to determine the account being reset. The backend must securely map the valid token to the specific user account that requested it.