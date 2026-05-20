## Metadata

- **Difficulty:** Practitioner
- **Category:** Path traversal
- **Lab URL:** [Lab: File path traversal, validation of start of path](https://portswigger.net/web-security/file-path-traversal/lab-validate-start-of-path)
- **Date Solved:** 14/5/2026
## Vulnerability Summary

The app tries to guard against path traversal attacks by transmitting the full path via a request parameter and validates that the supplied path starts with the expected folder. However, it reveals the folder hierarchy of the system and does not stop traversal sequences, allowing us to perform plain path traversal to read arbitrary files.
## Reconnaissance

The request to open a product image in new tab has the HTTP header in the form of `GET /image?filename=/var/www/images/30.jpg`. Removing any component of the path `/var/www/images/` will result in a `400 Bad Request` HTTP Response that reads `"Missing parameter 'filename'"`. 

However, if we add a traversal sequence after the path and send the request: `GET /image?filename=/var/www/images/../30.jpg`, we still get a `400 Bad Request` HTTP Response but with a different response message `"No such file"`. This suggests that path traversal is possible.
## Exploitation Steps

1. Click the "View details" button on any random item.
2. As you get to the product page (with URL something like `url/product?productId=2`), right click on the product image and select "Open Image in New Tab". Intercept the request to open the image in new tab.
3. The intercepted request's HTTP header would be in the form of `GET /image?filename=/var/www/images/30.jpg`. Modify the value of the `filename` field to `GET /image?filename=/var/www/images/../../../etc/passwd` and send the request.
4. Observe that the HTTP response has a status code `200 OK` and returns the contents of the `/etc/passwd` file. Lab is solved.
## Payload Used

`/var/www/images/../../../etc/passwd`
Since the only validation mechanism implemented to guard against path traversal is checking the literal string of the supplied path if it starts with an expected folder and not resolving the absolute path using the filesystem API, it is trivial to perform path traversal using traversal sequences after supplying the `filename` parameter with the expected file path.
## Root Cause

The application implements incomplete validation by only verifying that the user-supplied string begins with an expected base directory prefix (`/var/www/images/`). It fails to canonicalize the input path prior to validation and before passing it to the filesystem API. Consequently, the application trusts the prefix and passes the entire string to the operating system, which natively resolves the appended traversal sequences (`../`), allowing navigation outside the intended web root.
## Remediation

- Instead of attempting to strip/sanitize malicious input or checking the path (which is prone to bypasses), resolve the absolute path using the filesystem API before accessing the file to verify the resolved canonical path isn't something unexpected. 
- Avoid passing user-supplied input directly to filesystem APIs. Use an indirect object reference map (e.g., storing a database mapping where id=13 corresponds to image13.jpg on the server)
- If direct file references are unavoidable, validate user input against a strict whitelist of permitted characters (e.g., strictly alphanumeric). Reject any request containing path separators (`/`, `\`), traversal characters (`.`), or encoding indicators (`%`) outright.