## Metadata

- **Difficulty:** Expert
- **Category:** Authentication
- **Lab URL:** [Lab: Broken brute-force protection, multiple credentials per request](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request)
- **Date Solved:** 6/5/2026
## Vulnerability Summary

The app's brute force protection mechanism is flawed. Specifically, after the JSON parser deserializes the request payload, the backend insecurely accepts data types other than `String`, allowing us to pass an `array/list` onto the `password` parameter, bypassing the brute force defensive mechanisms which only operate at a HTTP transaction level.
## Reconnaissance

- Try logging in with invalid credentials, we see that the app performs account lockout after 3 incorrect attempts, returning `You have made too many incorrect login attempts. Please try again in 1 minute(s).` 
- Try adding a `X-Forwarded-For` header in the request and changing the value (IP address) of this field for different attempts, we see that the app still performs the same account lockout mechanism. This suggests that `HTTP` header supplementing does not work.
- Instead of the standard `Content-Type: application/x-www-form-urlencoded` for login forms, `JSON` is the data format used in this request body with `Content-Type: application/json`. Maybe we can find a way to supply multiple passwords in one single request to bypass the bruteforce protections?
## Exploitation Steps

1. Navigate to `url/login`. Intercept the request to login with credentials `carlos - randomvalue`.
2. Run the [Script to prepare an array of password candidates](arrayprep.py). You shall get an array that contains all of the password candidates in valid JSON format ready to be pasted
```
[
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    ...
]
```
3. Copy this output and paste it onto the `password` parameter in the request body. **Delete** the comma next to the last password on the array. Then, send the request. You should receive a `302 Found` HTTP Response, indicating a redirection has occurred. Right click on this response, select `View response in browser` and paste the copied URL onto the browser. You should see that you've successfully logged in as `carlos`, and lab is solved.
```
{
 "username":"carlos",
 "password": [
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    ...
]}
```
## Payload Used

[Candidate password list](../candidatepasswords.txt) (provided by PortSwigger)
```
{
 "username":"carlos",
 "password": [
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    ...
]}
```
The JSON parser, in the process of deserializing the payload, insecurely accepts the `array` data structure instead of strict enforcing a `String`. It in turn passes this list to the flawed authentication function in the backend, which either perform a simple loop to compare the hashed value of our password candidates to the stored credentials, or a SQL query. Either way, if the correct password exists in the list, the app grants access and logs us in.
## Root Cause

The absence of strict schema validation during the JSON deserialization phase, which results in unintended type casting. More specifically, instead of strictly enforcing a `String` data type for the `password` parameter, the backend accepts an `array`. Coupled with the flawed brute force protection mechanism that only relies on counting HTTP requests rather than the actual password verification attempts, we can gain access to any arbitrary user's account without knowing the password.
## Remediation

- Configure the JSON parser to enforce strict schema validation. The `password` parameter must be explicitly typed to accept only a `String` primitive. The backend must immediately reject requests containing any other data types, e.g. Arrays, Objects, or Null values for this field.
- Brute-force protection must evaluate the number of password verification attempts per user account at the application logic layer, rather than solely relying on counting HTTP requests at the middleware/WAF layer.
