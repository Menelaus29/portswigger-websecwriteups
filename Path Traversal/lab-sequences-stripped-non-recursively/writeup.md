## Metadata

- **Difficulty:** Practitioner
- **Category:** Path traversal
- **Lab URL:** [Lab: File path traversal, traversal sequences stripped non-recursively](https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively)
- **Date Solved:** 14/5/2026
## Vulnerability Summary

The app guards against directory traversal using traversal sequences (`../`) stripping. However, this stripping process is done non-recursively, as in the function iterates through the file name once, strip instances of `../`, and passes the filename onto the backend after it reaches the end. This is a flawed mechanism, as it allows us to use nested traversal sequences that revert to simple traversal sequences when the inner one is stripped, achieving directory traversal to read arbitrary files. 
## Reconnaissance

The request to open a product image in new tab has the HTTP header in the form of `GET /image?filename=6.jpg`. Changing the `filename` field's value to another file,  `/etc/passwd` (absolute path) or `../../../etc/passwd`, we get a `400 Bad Request` HTTP response that reads `No such file` in the response message. 
Using nested traversal sequences `....//` to supply the `filename` parameter: `....//....//....//etc/passwd` yields a `200 OK` HTTP Response with the contents of `/etc/passwd` in the response body. This suggests that the app does have traversal sequences stripping mechanism, but only does so non-recursively.
## Exploitation Steps

1. Click the "View details" button on any random item.
2. As you get to the product page (with URL something like `url/product?productId=2`), right click on the product image and select "Open Image in New Tab". Intercept the request to open the image in new tab.
3. The intercepted request's HTTP header would be in the form of `GET /image?filename=13.jpg`. Modify the value of the `filename` field to `....//....//....//etc/passwd` and send the request.
4. Observe that the HTTP response has a status code `200 OK` and returns the contents of the `/etc/paswd` file. Lab is solved.
## Payload Used

`....//....//....//etc/passwd`
The `../` means to step up one level in the directory structure. However, since the app performs traversal sequences stripping non-recursively, we must find a way to make the sequence exist even after the stripping process. Nesting them with `....//` ensure that after the inner sequence is stripped, the remaining characters make a valid traversal sequence, thus passing the payload `../../../etc/passwd` to the filesystem.  
## Root Cause

The application implements a flawed input sanitization mechanism that relies on a single-pass string replacement function to strip path traversal sequences. Because the sanitization is not performed recursively or iteratively until the string state stops changing, an attacker can nest traversal sequences (`....//`). When the inner `../` is stripped, the remaining characters form a valid `../` sequence, bypassing the filter and allowing arbitrary file reads.
## Remediation

- Avoid passing user-supplied input directly to filesystem APIs. Use an indirect object reference map (e.g., storing a database mapping where id=13 corresponds to image13.jpg on the server)
- If direct file references are unavoidable, validate user input against a strict whitelist of permitted characters (e.g., strictly alphanumeric). Reject any request containing path separators (`/`, `\`), traversal characters (`.`), or encoding indicators (`%`) outright.
- Resolve the absolute path using the filesystem API before accessing the file to verify the resolved canonical path isn't something unexpected.
- If input sanitization is strictly required by legacy architecture, the stripping function must execute recursively (e.g., via a `while` loop) until no (unexpected) instances of `../` or `..\` remain in the input string.