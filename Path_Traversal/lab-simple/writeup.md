## Metadata

- **Difficulty:** Apprentice
- **Category:** Path traversal
- **Lab URL:** [Lab: File path traversal, simple case](https://portswigger.net/web-security/file-path-traversal/lab-simple)
- **Date Solved:** 20/4/2026
## Vulnerability Summary

The app has no defensive mechanisms against path traversal attacks. Specifically, in the `url/image?filename=`, it is possible to inject a payload that traverses through directories to retrieve information from sensitive, meant-to-be-inaccessible files.
## Reconnaissance

- The request to open a product image in new tab has the HTTP header in the form of `GET /image?filename=6.jpg`. Changing the `filename` field's value to another file, e.g. `etc/passwd`, we get a `400 Bad Request` HTTP response that reads `No such file` in the response message. We get the same response with `../etc/passwd`. This confirms that we can access other files in the file system, and directory traversal is possible.
## Exploitation Steps

1. Click the "View details" button on any random item.
2. As you get to the product page (with URL something like `url/product?productId=2`), right click on the product image and select "Open Image in New Tab". Intercept the request to open the image in new tab with Burp Suite proxy.
3. The intercepted request's HTTP header would be in the form of `GET /image?filename=6.jpg`. Modify the value of the `filename` field to `../../../etc/passwd`. 
4. Observe that the HTTP response has a status code `200 OK` and returns the contents of the `etc/paswd` file. Lab is solved.
## Payload Used

`../../../etc/passwd`
The `../` means to step up one level in the directory structure. Through trial and error (trying `../etc/passwd` and `../../etc/passwd` first), we find that the `etc/passwd` file is 3 levels up in the directory hierarchy compared to the directory that contains images for items.
## Root Cause

The application takes user-supplied input via the `filename` parameter and appends it directly to a base directory path to interact with a filesystem API (e.g., to read the image file). The vulnerability exists because the application fails to validate, sanitize, or canonicalize this input, allowing malicious directory traversal sequences (`../`) to escape the intended web root and access arbitrary files on the underlying server.
## Remediation

- Avoid passing user-supplied input directly to filesystem APIs. Use an indirect object reference map (e.g., storing a database mapping where id=6 corresponds to image6.jpg on the server)
- Validate user input with a whitelist without processing it
- Resolve the absolute path using the filesystem API before accessing the file to verify the resolved canonical path isn't something unexpected.