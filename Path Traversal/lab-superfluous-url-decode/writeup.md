## Metadata

- **Difficulty:** Practitioner
- **Category:** Path traversal
- **Lab URL:** [Lab: File path traversal, traversal sequences stripped with superfluous URL-decode](https://portswigger.net/web-security/file-path-traversal/lab-superfluous-url-decode)
- **Date Solved:** 14/5/2026
## Vulnerability Summary

The application is vulnerable to file path traversal because it strips traversal sequences (`../`) before performing a final URL-decode on the user input. By double URL-encoding the traversal payload, an attacker can bypass the initial sanitization filter. The backend then decodes the payload back into standard directory traversal sequences, allowing arbitrary file read access on the server.
## Reconnaissance

The request to open a product image in new tab has the HTTP header in the form of `GET /image?filename=6.jpg`. Changing the `filename` field's value to another file,  `/etc/passwd` (absolute path) or `../../../etc/passwd`, we get a `400 Bad Request` HTTP response that reads `No such file` in the response message. Same response can be observed when we try to nest the traversal sequences, or URL encode the characters `E` and `F` once. However, URL-encoding them twice: `../` to `%2E%2E%2F` to `%2%45%2%45%2F` (`%45` = `E` URL encoded) yields a `200 OK` HTTP Response with the contents of `/etc/passwd` in the response body.
## Exploitation Steps

1. Click the "View details" button on any random item.
2. As you get to the product page (with URL something like `url/product?productId=2`), right click on the product image and select "Open Image in New Tab". Intercept the request to open the image in new tab.
3. The intercepted request's HTTP header would be in the form of `GET /image?filename=13.jpg`. Modify the value of the `filename` field to `%2%45%2%45%2F%2%45%2%45%2F%2%45%2%45%2Fetc%2Fpasswd` 
4. Observe that the HTTP response has a status code `200 OK` and returns the contents of the `/etc/paswd` file. Lab is solved.
## Payload Used

`%2%45%2%45%2F%2%45%2%45%2F%2%45%2%45%2Fetc%2Fpasswd` 
**Note**: the industry-standard approach to double URL-encoding is to encode the `%` sign as `%25`.
A more accurate and practical payload would be
`%252E%252E%252F%252E%252E%252F%252E%252E%252Fetc%252Fpasswd`

| Character | URL Encoding (UTF-8) |
| --------- | -------------------- |
| .         | %2E                  |
| /         | %2F                  |
| E         | %45                  |
| %         | %25                  |
When the security filter inspects the input, it sees `%252E%252E%252F` and finds no literal `../` or `%2E%2E%2F` to strip. The backend subsequently performs a superfluous decode operation, transforming the input into `../../../etc/passwd` prior to passing it to the filesystem API.
## Root Cause

The vulnerability exists due to a flawed order of operations in the application's input validation logic. The application sanitizes the user input (stripping `../`) _before_ the input is fully decoded by the application framework. A superfluous decoding step is applied after the security controls had already been executed, allowing encoded malicious input to bypass the filter and manifest during execution.
## Remediation

- Remove any superfluous, manual URL decoding operations in the application logic. Let the web application framework handle initial URL decoding.
- Instead of attempting to strip or sanitize malicious input (which is prone to bypasses), resolve the absolute path using the filesystem API before accessing the file to verify the resolved canonical path isn't something unexpected. 
- Avoid passing user-supplied input directly to filesystem APIs. Use an indirect object reference map (e.g., storing a database mapping where id=13 corresponds to image13.jpg on the server)
- If direct file references are unavoidable, validate user input against a strict whitelist of permitted characters (e.g., strictly alphanumeric). Reject any request containing path separators (`/`, `\`), traversal characters (`.`), or encoding indicators (`%`) outright.