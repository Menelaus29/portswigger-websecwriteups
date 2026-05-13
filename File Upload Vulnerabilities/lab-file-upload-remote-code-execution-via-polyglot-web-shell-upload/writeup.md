## Metadata

- **Difficulty:** Practitioner
- **Category:** File Upload Vulnerabilities
- **Lab URL:** [Lab: Remote code execution via polyglot web shell upload](https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-polyglot-web-shell-upload)
- **Date Solved:** 13/5/2026
## Vulnerability Summary

The app contains a vulnerable image upload function. Though it does attempt to check the contents (presumably the magic bytes) of files to ensure that they are genuine image, this defense mechanism can be bypassed by using [ExifTool](https://exiftool.org/) to manipulate the file's metadata to create a `.php` file with `.jpg`'s magic bytes. This allows us to upload our executable PHP web shell to run our commands.
## Reconnaissance

After navigating to `url/login` and logging in with credentials `wiener - peter`, we are taken to `url/my-account?id=wiener`, and are presented an option to upload an image as our avatar. Try uploading a [PHP web shell](../shell.php) right away will result in a `403 Forbidden` HTTP Response that, in the response body, reads `Error: file is not a valid image`.

Modifying the value of the `Content-Type` header in the HTTP request to `image/jpeg` and sending it again, we see the same response as before. Same response can be observed when we add `.jpg` as a file extension to the `filename` parameter.

We need to find a way to bypass the magic bytes check. I used [ExifTool](https://exiftool.org/) to inject a simple PHP shell into the metadata of a normal image then saved the file as a `.php` file. Uploading this file will yield a `200 OK` HTTP Response that reads `The file avatars/polyglot.php has been uploaded.`.Opening this uploaded file with `GET /file/avatars/polyglot.php` results in a `200 OK` HTTP Response with our secret string and the contents of the image in the response. Our shell has successfully been executed. 
## Exploitation Steps

1. Navigate to `url/login` and login with the credentials `wiener - peter`.
2. Use [ExifTool](https://exiftool.org/) to run `exiftool -Comment="<?php echo 'START ' . file_get_contents('/home/carlos/secret') . ' END'; ?>" img.jpg -o polyglot.php`. A file named `polygot.php` will be created in the same folder.
3. Upload this file using the upload avatar function. You should receive a `200 OK` HTTP Response that reads `The file avatars/polyglot.php has been uploaded.`
4. On `url/my-account?id=wiener`, right click on your "avatar" and select "Open Image in New Tab". You'll be taken to `url/files/avatars/polyglot.php`. Observe that at the first line of the response body, between the `START` and `END`, there's a string - this is the "secret". Copy this string and submit, lab is solved.
## Payload Used

`Exiftool` command: `exiftool -Comment="<?php echo 'START ' . file_get_contents('/home/carlos/secret') . ' END'; ?>" img.jpg -o polyglot.php`

This command injects a PHP payload to read the content of `/home/carlos/secret` into JPEG's EXIF `Comment` metadata field. The content is put in between `START` and `END`. The `img.jpg` is the source to inject the payload, in order to ensure that the output retains valid JPEG magic bytes, bypassing the file content validation.
## Root Cause

The vulnerability exists due to two server-side misconfigurations. First, the application validates uploaded files relying exclusively on file signatures (magic bytes) without validating the file extension, allowing a `.php` file to pass validation if it leads with JPEG bytes. Second, the application stores these uploads in a directory where the web server is configured to execute server-side scripts, rather than serving them strictly as static assets.
## Remediation

- Do not save user-supplied files directly. Process incoming images using a robust image processing library (e.g., PHP GD or ImageMagick) to recreate the image and strip all EXIF data, nullifying polyglot payloads.
- Validate the file extension against a hardcoded whitelist of permitted image types (e.g., `.jpg`, `.png`). Deny any request containing executable extensions or double extensions.
- Modify the web server configuration (e.g., via `.htaccess` in Apache or location blocks in Nginx) to explicitly deny the execution of server-side scripts  within the upload directory.
- Never use user-supplied filenames on the filesystem. Generate a secure, random identifier (e.g., UUID) for the stored file.