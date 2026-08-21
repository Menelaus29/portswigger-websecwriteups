## Metadata

- **Difficulty:** Apprentice 
- **Category:** OS Command Injection
- **Lab URL:** [Lab: OS command injection, simple case](https://portswigger.net/web-security/os-command-injection/lab-simple)
- **Date Solved:** 21/08/2026
## Vulnerability Summary

The app contains an OS command injection vulnerability in the product stock check functionality. The app uses the user-supplied input to executes a shell command without validation or sanitization, and the raw output is returned in the response. We can exploit this to execute arbitrary OS commands.
## Reconnaissance

Per the description of the lab, "The application executes a shell command containing user-supplied product and store IDs, and returns the raw output from the command in its response." If this user-supplied input is not validated or sanitized before using, we can inject arbitrary OS commands to execute them.
## Exploitation Steps

1. Click on the "View details" button under any random item. You will be taken to `url/product?productId=[number]`.
2. Intercept the request where you click "Check stock" (`POST /product/stock`) with Burp Suite proxy, then send it to Burp Suite Repeater.
3. Modify the value of the `storeId` parameter to `storeId=1;whoami`
4. Send the request. The name of the current user should appear on the response, and lab is solved.
## Payload Used

`storeId=1;whoami`
Since the app executes a shell command with the user supplied input (particularly `productId` and `storeId`) without any validation or sanitization, we can introduce a semicolon `;` to chain the bash command `whomai` with the previous legitimate command. Our injected command is executed regardless of if the previous one success or not.
## Root Cause

The app blindly trusts user-supplied input to execute bash command without validation or sanitization.
## Remediation

The app should never invoke OS commands directly using user-supplied input. Instead, it should use built-in library functions or APIs (e.g., querying the backend database directly for stock levels) to achieve the required functionality.
If calling out to an external OS command is strictly unavoidable:
- Implement strict input validation using a whitelist (e.g., validate that `productId` and `storeId` contain only numeric characters).
- Never pass user input to a shell interpreter (like `system()` or `popen()`). Instead, use parameterized execution APIs (like `subprocess.run()` in Python with `shell=False`, or `execFile` in Node.js) that execute the binary directly and pass user input safely as arguments.