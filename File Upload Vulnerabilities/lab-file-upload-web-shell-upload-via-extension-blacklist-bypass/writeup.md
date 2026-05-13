## Metadata

- **Difficulty:** Practitioner
- **Category:** File Upload Vulnerabilities
- **Lab URL:** [Lab: Web shell upload via extension blacklist bypass](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass)
- **Date Solved:** 13/5/2026
## Vulnerability Summary

The app contains a vulnerable image upload function. Though it does attempt to block the upload of files using a blacklist, this blacklist can be overridden by uploading our own `.htaccess` file, allowing us to trick the server into mapping an arbitrary, custom file extension to an execute MIME type, `application/x-httpd-php` in this case. This permits us to successfully upload our own executable web shell on the server, thus granting us the ability to run any commands.
## Reconnaissance

After navigating to `url/login` and logging in with credentials `wiener - peter`, we are taken to `url/my-account?id=wiener`, and are presented an option to upload an image as our avatar. Try uploading a [PHP web shell](../shell.php) right away will result in a `403 Forbidden` HTTP Response that, in the response body, reads `Sorry, php files are not allowed`.

Try changing the file extension to `.php5` will result in a `200 OK` and successful upload. However, sending a HTTP request `GET /files/avatars/shell.php5` after that lead to a `304 Not Modified` response, with a non-usable shell.

I created a `.htaccess` [file](.htaccess), with the hope of overriding the server's configuration. The file's content is as follows:
`AddType application/x-httpd-php .aaa`
It makes `.aaa` files be interpreted as `.php` files. Uploading this file will give us a `200 OK`, and message `The file avatars/.htaccess has been uploaded.`. Now we try to upload the web shell again, this time changing the file extension from `.php` to `.aaa`. This time, we get a `200 OK`, and the message `The file avatars/shell.aaa has been uploaded.`.  Try accessing this file through `GET /files/avatars/shell.aaa` will result in a `200 OK` HTTP Response, with an executable web shell. We have successfully uploaded a web shell.
## Exploitation Steps

**Note**: `.aaa` is just an arbitrary custom file extension that I chose to be interpreted as `.php`. You can pick any custom file extension you like.

1. Navigate to `url/login` and login with the credentials `wiener - peter`.
2. Create a `.htaccess` file with content that reads `AddType application/x-httpd-php .aaa`. Upload this file onto the server with the upload avatar function. Observe that you received a `200 OK` HTTP Response with the message `The file avatars/.htaccess has been uploaded.`.
3. On our [PHP web shell](../shell.php), change the file extension from `.php` to `.aaa` while leaving its content unchanged. Upload this file through the avatar upload function. Observe that you received a `200 OK` HTTP Response with the message `The file avatars/shell.aaa has been uploaded.`.
4. On `url/my-account?id=wiener`, right click on your "avatar" and select "Open Image in New Tab". Observe that you have a working shell.
5. Run `cat /home/carlos/secret` to exfiltrate the contents of the file `/home/carlos/secret`. The app will return a string - this is the "secret". Copy this string and submit solution, lab is solved.
## Payload Used

`.htaccess` file: `AddType application/x-httpd-php .aaa`
[PHP web shell](../shell.php) (named `shell.aaa`) in this lab
This maps our custom file extension (`.aaa`) to the executable MIME type `application/x-httpd-php`, thus configuring the server to interpret `.aaa` files as `.php` ones, tricking the server to execute our web shell written in `PHP` with a modified extension. 
## Root Cause

The app is vulnerable due to a flawed file upload implementation that relies on a blacklisting approach for file extensions and fails to restrict the upload of server configuration files. The app explicitly blocked known executable extensions (`.php`), but permitted the upload of `.htaccess` files into the web root. This allows an attacker to override Apache server configurations at the directory level and arbitrarily map harmless extensions to the PHP executable MIME type.
## Remediation

- User-uploaded files should be stored in a directory that is not directly accessible or executable via the web server.
- Reject any file extension that is not explicitly permitted (e.g., allow only `.jpg`, `.png`). Do not rely on blacklists.
- Strictly prohibit the upload of server configuration files such as `.htaccess`, `.user.ini`, or `web.config`.
- Verify the file signature (magic bytes) to ensure the uploaded file matches its expected MIME type, rather than trusting the user-supplied `Content-Type` header or extension.
- Configure the web server to explicitly deny execution of server-side scripts in the upload folder (e.g., using `php_flag engine off` in Apache or turning off execution privileges in Nginx).
