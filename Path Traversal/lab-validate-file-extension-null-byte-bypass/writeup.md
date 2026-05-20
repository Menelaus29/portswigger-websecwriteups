## Metadata

- **Difficulty:** Practitioner
- **Category:** Path traversal
- **Lab URL:** [Lab: File path traversal, validation of file extension with null byte bypass](https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass)
- **Date Solved:** 14/5/2026
## Vulnerability Summary

The app tries to guard against path traversal attacks by validating that the supplied filename ends with the expected file extension. However, this defense mechanism can be easily bypassed using a null byte (`%00`) to exploit a string parsing discrepancy between the app's input validation logic and the underlying operating system's filesystem APIs, allowing path traversal.
## Reconnaissance

As the description of the lab suggests, the app validates that the supplied filename ends with the `.jpg`. We can look for a string parsing discrepancy between the app's input validation logic which, written in a high-level language, might use length-prefixed strings compared to null-terminated used by the OS's filesystem APIs. Thus, we can try to append a null byte `%00` right before adding `.jpg` at the end of our payload. 
## Exploitation Steps

1. Click the "View details" button on any random item.
2. As you get to the product page (with URL something like `url/product?productId=2`), right click on the product image and select "Open Image in New Tab". Intercept the request to open the image in new tab.
3. The intercepted request's HTTP header would be in the form of `GET /image?filename=9.jpg`. Modify the value of the `filename` field to `GET /image?filename=../../../etc/passwd%00.jpg` and send the request.
4. Observe that the HTTP response has a status code `200 OK` and returns the contents of the `/etc/passwd` file. Lab is solved.
## Payload Used

`../../../etc/passwd%00.jpg`

- `../../../etc/passwd`: Traverses up the directory tree to target the sensitive OS file. 
- `%00`: Injects a null byte, acting as a string terminator for the underlying OS. 
- `.jpg`: Satisfies the application's whitelisted extension validation check.
## Root Cause

The application, presumably based on a high-level language, uses length-prefixed strings. Thus, when validating the file extension, it reads the entire string `/../../../etc/passwd%00.jpg` and passes the whitelist check (since the extension it identifies is `.jpg`). It passes this filename to the underlying filesystem functions., where the string is handed to the OS's `C` standard library, which uses null-terminated strings. It reads `../../../etc/passwd`, hits the null byte `%00`, and interprets this as the end of the string, discarding `.jpg`. The app also does not guard against path traversal sequences.
## Remediation

- Instead of attempting to strip/sanitize malicious input or checking the path (which is prone to bypasses), resolve the absolute path using the filesystem API before accessing the file to verify the resolved canonical path isn't something unexpected. 
- Avoid passing user-supplied input directly to filesystem APIs. Use an indirect object reference map (e.g., storing a database mapping where id=13 corresponds to image13.jpg on the server)
- If direct file references are unavoidable, validate user input against a strict whitelist of permitted characters (e.g., strictly alphanumeric). Reject any request containing path separators (`/`, `\`), traversal characters (`.`), or encoding indicators (`%`) outright.