## Metadata

- **Difficulty:** Practitioner
- **Category:** Path traversal
- **Lab URL:** [Lab: File path traversal, traversal sequences blocked with absolute path bypass](https://portswigger.net/web-security/file-path-traversal/lab-absolute-path-bypass)
- **Date Solved:** 14/5/2026
## Vulnerability Summary

The app contains a path traversal vulnerability in the display of product images. Specifically, in `url/image?filename=`, it is possible to inject file names to retrieve information from those sensitive, meant-to-be-inaccessible files.
## Reconnaissance

- The request to open a product image in new tab has the HTTP header in the form of `GET /image?filename=13.jpg`. Changing the `filename` field's value to another file, e.g. `/etc/passwd`, we get a `200 OK` HTTP response with the content of `/etc/passwd`. This suggests that we can inject the absolute path from the filesystem root of any file into the parameter `filename` to get the contents of that file.
## Exploitation Steps

1. Click the "View details" button on any random item.
2. As you get to the product page (with URL something like `url/product?productId=2`), right click on the product image and select "Open Image in New Tab". Intercept the request to open the image in new tab.
3. The intercepted request's HTTP header would be in the form of `GET /image?filename=13.jpg`. Modify the value of the `filename` field to `/etc/passwd`. 
4. Observe that the HTTP response has a status code `200 OK` and returns the contents of the `/etc/paswd` file. Lab is solved.
## Payload Used

`/etc/passwd`
The application strips or blocks relative path traversal sequences (e.g., `../`), but it fails to sanitize absolute file paths. Because the backend code treats the input as a direct file path and processes absolute paths natively, starting the payload with `/` bypasses the relative traversal filter and accesses the file directly from the filesystem root.
## Root Cause

The application lacks explicit validation against absolute path inputs. It passes input directly to a filesystem API that natively resolves absolute paths (e.g., overriding the intended base directory), granting direct read access to the filesystem root.
## Remediation

- Avoid passing user-supplied input directly to filesystem APIs. Use an indirect object reference map (e.g., storing a database mapping where id=13 corresponds to image13.jpg on the server)
- Validate user input with a whitelist without processing it
- Resolve the absolute path using the filesystem API before accessing the file to verify the resolved canonical path isn't something unexpected.