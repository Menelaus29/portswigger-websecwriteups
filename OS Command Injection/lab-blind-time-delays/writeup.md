## Metadata

- **Difficulty:** Practitioner
- **Category:** OS Command Injection
- **Lab URL:** [Lab: Blind OS command injection with time delays](https://portswigger.net/web-security/os-command-injection/lab-blind-time-delays)
- **Date Solved:** 21/08/2026
## Vulnerability Summary

The app contains a blind OS Command Injection vulnerability in the feedback function. The app executes shell command containing the user-supplied input without any sanitization or validation. Although the output is not reflected in the response, we can inject a time-based payload to confirm the vulnerability.
## Reconnaissance

- Click on the "Submit feedback" button and input random legitimate values. Intercept this request (`POST /feedback/submit`). The response should contain the following line (`csrf-token` is randomized):
```
csrf=csrf-token&name=1&email=1&subject=1&message=1
```
- Try injecting each of the parameter with `;whoami` results in a `500 Internal Server Error` response, which suggests that `;whoami` is not treated as a mere string. (One of) these parameter(s) may be vulnerable to OS command injection.
## Exploitation Steps

1. Click on the "Submit feedback" button and input random values. Intercept this request.
2. Append this payload into all 4 of the parameters (`name`, `email`, `subject`, `message`): `;ping%20-c%2010%20127.0.0.1;`. Submit the request.
3. You should get a response after approximately 10 seconds, which proves that the OS command got executed on the backend. Lab should be marked as solved.
(On further testing, the `email` parameter is the vulnerable one).
## Payload Used

`;ping%20-c%2010%20127.0.0.1;`
This payload is basically a OS command in Unix/Linux environments, `ping -c 10 127.0.0.1` (the `%20` is the space character URL-encoded). This command instructs the server to send 10 ICMP echo requests to its own loopback address (`127.0.0.1`). Because the `ping` utility sends one request per second, 10 of them is gonna take around 10 seconds, which is exactly the delay observed between the time we send the request and we receive the response. The 2 appended and prepended semicolons `;` are used to concatenate any commands before and after our payload, preventing a syntax error.
## Root Cause

The app blindly trusts user-supplied input to execute bash command without validation or sanitization.
## Remediation

The app should never invoke OS commands directly using user-supplied input. Instead, it should use built-in library functions or APIs (e.g., querying the backend database directly for stock levels) to achieve the required functionality.
If calling out to an external OS command is strictly unavoidable:
- Implement strict input validation using a whitelist (e.g., validate that the input fields only contains alphanumeric characters).
- Never pass user input to a shell interpreter (like `system()` or `popen()`). Instead, use parameterized execution APIs (like `subprocess.run()` in Python with `shell=False`, or `execFile` in Node.js) that execute the binary directly and pass user input safely as arguments.