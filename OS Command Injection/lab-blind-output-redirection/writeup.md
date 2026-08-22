## Metadata

- **Difficulty:** Practitioner
- **Category:** OS Command Injection
- **Lab URL:** [Lab: Blind OS command injection with output redirection](https://portswigger.net/web-security/os-command-injection/lab-blind-output-redirection)
- **Date Solved:** 22/08/2026
## Vulnerability Summary

The app contains a blind OS Command Injection vulnerability in the feedback function. The app executes shell command containing the user-supplied input without any sanitization or validation. Although the output is not reflected in the response, we can write (redirect) the output of the injected command into a retrievable file within the web root to view it there.
## Reconnaissance

- Click on the "Submit feedback" button and input random legitimate values. Intercept this request (`POST /feedback/submit`). The response should contain the following line (`csrf-token` is randomized):
```
csrf=csrf-token&name=1&email=1&subject=1&message=1
```
 - Per the lab's description, "There is a writable folder at: `/var/www/images/`. The application serves the images for the product catalog from this location." As the output from the shell command executed by the backend is not returned in the response, we can inject a command and write the output to the writable folder, then retrieve it through the image serving functionality. 
## Exploitation Steps

1. Click on the "Submit feedback" button and input random values. Intercept this request.
2. Append this payload into all 4 of the parameters (`name`, `email`, `subject`, `message`): `;whoami%20>/var/www/images/whoami.txt;`. Submit the request.
3. After receiving the response, click on the "View details" button under any random item. You will be taken to `url/product?productId=[number]`. Reload the page. In your HTTP history, there should be a request from the app to serve the image for the product, with the request line that looks like: `GET /image?filename=12.jpg`. Change the value of the `filename` parameter to `whoami.txt`. The response should return the OS user, and lab is solved.
(On further testing, the `email` parameter is the vulnerable one).
## Payload Used

`;whoami%20>/var/www/images/whoami.txt;`
`GET /image?filename=whoami.txt`
The OS command `whoami >/var/www/images/whoami.txt` (`%20` is the space character URL-encoded) executes the `whoami` command and, with `>`, sends the output to the specified file `/var/www/images/whoami.txt`. Our remaining task is trivial - we only need to find the request of the app's image serving functionality and change the parameter to our filename `whoami.txt` to retrieve it.
## Root Cause

The app blindly trusts user-supplied input to execute bash command without validation or sanitization. Also, any user can write anything into the folder `/var/www/images/` and retrieve it through the `/image?filename=` endpoint.
## Remediation

The app should never invoke OS commands directly using user-supplied input. Instead, it should use built-in library functions or APIs (e.g., querying the backend database directly for stock levels) to achieve the required functionality.
If calling out to an external OS command is strictly unavoidable:
- Implement strict input validation using a whitelist (e.g., validate that the input fields only contains alphanumeric characters).
- Never pass user input to a shell interpreter (like `system()` or `popen()`). Instead, use parameterized execution APIs (like `subprocess.run()` in Python with `shell=False`, or `execFile` in Node.js) that execute the binary directly and pass user input safely as arguments.