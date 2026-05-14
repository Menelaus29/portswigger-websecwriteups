## Metadata

- **Difficulty:** Expert
- **Category:** File Upload Vulnerabilities
- **Lab URL:** [Lab: Web shell upload via race condition](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-race-condition)
- **Date Solved:** 13/5/2026
## Vulnerability Summary

The app contains a vulnerable image upload function. It performs validation on user-uploaded files by temporarily writing these files to a persistent location on the server, runs functions to check if they are in the extension whitelist, then deletes them on the server if they are not. This introduces a race condition vulnerability, where our injected shell can be executed on the short time it lives on the server before getting deleted.
## Reconnaissance

All the techniques used before in the labs of this same topic: adding `.jpg` at the end, adding a null character `%00`, changing `Content-Type` header, using ExifTool to inject the payload into the comment field of the meta of a legitimate image, path traversal... did not work.

The learning content that introduces this lab mentions that:
"For example, some websites upload the file directly to the main filesystem and then remove it again if it doesn't pass validation. This may only take a few milliseconds, but for the short time that the file exists on the server, the attacker can potentially still execute it.". Moreover, from the hint, we know that the part of the validation performed by the backend is as below:
```php
`<?php 
$target_dir = "avatars/"; 
$target_file = $target_dir . $_FILES["avatar"]["name"]; 
// temporary move 
move_uploaded_file($_FILES["avatar"]["tmp_name"], $target_file); 
if (checkViruses($target_file) && checkFileType($target_file)) { 
	echo "The file ". htmlspecialchars( $target_file). " has been uploaded."; 
} else { 
	unlink($target_file); 
	echo "Sorry, there was an error uploading your file."; 
	http_response_code(403); 
} 
function checkViruses($fileName) { 
	// checking for viruses 
	... 
} 
function checkFileType($fileName) { 
	...
}
?>
```
With `move_uploaded_file($_FILES["avatar"]["tmp_name"], $target_file);`, it is concrete that, any file we upload will exist on the server until both of the functions `checkViruses` and `checkFileType` are over, no matter what type it is. If files are insecurely configured to be executed, we can use this temporary existence to run our shell.
## Exploitation Steps

1. Navigate to `url/login` and login with the credentials `wiener - peter`.
2. Intercept the request to upload your PHP web shell (`POST /my-account/avatar`). Since the file will only exist on the server for a short period of time, the shell must be able to execute our command `cat /home/carlos/secret` immediately. Thus, unlike the fully functional shell where we are able to type in our commands used in the previous labs, the shell for this lab will be:
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
```
3. Upload a normal legitimate `jpg/png` file. Intercept the request to "Open Image in New Tab", then change the HTTP header of that request to `GET /files/avatars/test.php`.
4. Send the intercepted `GET`request to the Automate function in Caido. The idea is to automatically send these requests while sending a single `POST` request in order to exploit the race condition, executing our shell in the short period of time it exists on the server. Configure to run ~40 of these `GET` requests, then immediately after, send the `POST` request.
5. After the attack's finished, you should see that amidst the `404 Not Found` responses to the `GET` requests, there are some `200 OK` responses. These `200 OK` ones are when the file existed on the server, so the `GET` requests sent in this period could find the file. The response message of these responses will all contain a single string. This is the "secret" we are looking for. Copy this string and submit, lab is solved.

**Note:**
- Do not send a lot of `GET` requests in the 4th step - I got timeout sending ~300 requests.
## Payload Used

`PHP` shell:
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
```
The shell is pretty self explanatory - the most important part of this lab is the exploitation of race condition. Refer to the **Exploitation Steps** for the explanation on how that works.
## Root Cause

The file processing implemented by the server is flawed. Any file that is uploaded onto the server will be stored on the main filesystem temporarily until the validation functions are finished, then deleted after if they violate one of these validations. Thus, no matter how robust these validation mechanisms are, if we can find a way to execute our shell when it's stored on the server and currently going through validation, RCE is still possible.
## Remediation

The developer must ensure that uploaded files are never placed in a web-accessible directory before they have been fully verified. 
- Do not move the uploaded file to the `avatars/` directory at the start of the script. PHP automatically stores uploaded files in a secure, temporary system directory (e.g., `/tmp`) defined by the `upload_tmp_dir` directive in `php.ini`. Keep the file there during validation.
- Only execute `move_uploaded_file()` to transfer the file from the system temporary directory to the web-accessible `avatars/` directory *after* `checkViruses()` and `checkFileType()` return true.
- Configure the web server to disable server-side script execution in upload directories. For Apache, place an `.htaccess` file in the `avatars/` directory containing `php_flag engine off` or `<FilesMatch "\.php$"> Require all denied </FilesMatch>`. 
- Never use the user-supplied filename (through`$_FILES["avatar"]["name"]`) directly. Rename the file to a secure, randomly generated hash (e.g., UUID) upon storage to completely eliminate file path guessing during any processing window.