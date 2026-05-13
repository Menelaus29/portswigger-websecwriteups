## Metadata

- **Difficulty:** Practitioner
- **Category:** File Upload Vulnerabilities
- **Lab URL:** [Lab: Web shell upload via obfuscated file extension](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-obfuscated-file-extension)
- **Date Solved:** 13/5/2026
## Vulnerability Summary

The app contains a vulnerable image upload function. Though it does attempt to block certain file extensions through blacklisting, this defense mechanism can be bypassed by combining 2 obfuscation techniques: adding a URL-encoded null byte (`%00`) and a additional extension (`.jpg`), thus allowing us to upload our executable PHP web shell to run our commands.
## Reconnaissance

After navigating to `url/login` and logging in with credentials `wiener - peter`, we are taken to `url/my-account?id=wiener`, and are presented an option to upload an image as our avatar. Try uploading a [PHP web shell](../shell.php) right away will result in a `403 Forbidden` HTTP Response that, in the response body, reads `Sorry, only JPG & PNG files are allowed`.

Modifying the value of the `Content-Type` header in the HTTP request to `image-jpeg` and sending it again, we see the same response as before: `403 Forbidden`, `Sorry, only JPG & PNG files are allowed`. This suggests that the server does not implicitly trust the value of this header.

Modifying the file extension from `shell.php` to `shell.php.jpg` then sending the request results in a `200 OK` HTTP Response with the message `The file avatars/shell.php.jpg has been uploaded.`. However, when we try to open this file through `GET /files/avatars/shell.php.jpg`, we get a `304 Not Modified` HTTP Response with the message `The image url/files/avatars/shell.php.jpg cannot be displyed because it contains errors.`. 

Same approach as before, but this time we add a URL-encode null character before the `.jpg` to make the file string `shell.php%00.jpg`. This request yields a `200 OK` with the response message `The file avatars/shell.php has been uploaded.`, suggesting that the backend (at its filesystem functions) uses null-terminated strings. It read `shell.php`, hit the null character `%00`, thought that was the end of the string and discarded the rest (`.jpg`).  Opening this uploaded file with `GET /file/avatars/shell.php` results in a `200 OK` and a shell ready to execute commands. We have successfully uploaded our web shell. 
## Exploitation Steps

1. Navigate to `url/login` and login with the credentials `wiener - peter`.
2. Upload the [PHP web shell](../shell.php) like normal. Intercept this request.
3. On the intercepted request in Step 2, modify the `filename` parameter from `filename="shell.php"` to `filename="shell.php%00.jpg"`, and send the request again. Observe that the response has a status code of `200 OK` with the response message `The file avatars/shell.php has been uploaded.`
4. On `url/my-account?id=wiener`, right click on your "avatar" and select "Open Image in New Tab". You'll be taken to `url/files/avatars/shell.php%00.jpg`, where it says `The requested URL was not found on this server` and returns `404 Not Found`. Manually modify the URL to `url/files/avatars/shell.php`. Observe that you have a working shell now.
5. Run `cat /home/carlos/secret` to exfiltrate the contents of the file `/home/carlos/secret`. The app will return a string - this is the "secret". Copy this string and submit, lab is solved.
## Payload Used

`filename="shell.php%00.jpg"`
`GET /files/avatars/shell.php HTTP/1.1`
[PHP web shell](../shell.php)
Command to read the secret string: `cat /home/carlos/secret`.

The application, presumably based on a high-level language, uses length-prefixed strings. Thus, when validating the file extension, it reads the entire string `shell.php%00.jpg` and passes the whitelist check (since the extension it identifies is `.jpg`). It passes this filename to the underlying filesystem functions., where the string is handed to the OS's `C` standard library, which uses null-terminated strings. It reads `shell.php`, hits the null byte `%00`, and interprets this as the end of the string, discarding `.jpg`. The file is written to the disk as `shell.php`.
## Root Cause

The vulnerability stems from a string parsing discrepancy between the app's input validation logic and the underlying operating system's filesystem APIs. The app, written in a high-level language, processes the filename as a length-prefixed string, evaluating the entire input (`shell.php%00.jpg`) and successfully validating the `.jpg` extension. However, when the application passes this filename to the OS-level filesystem functions (which rely on C standard libraries), the string is read as null-terminated. The API stops reading at the null byte (`%00`), truncating the filename to `shell.php` and writing an executable script to the disk.
## Remediation

- Strip all null bytes (`0x00`) and control characters from user-supplied filenames before any validation or processing occurs.
- Never use user-supplied filenames on the filesystem. Generate a secure, random identifier (e.g., UUID) for the stored file.
- Validate the file extension against a strict whitelist after sanitization.
- Store uploaded files in a directory located outside of the web root. If files must be served from within the web root, configure the web server to explicitly deny script execution in that directory.