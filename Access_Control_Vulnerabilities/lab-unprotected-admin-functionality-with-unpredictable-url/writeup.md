## Metadata

- **Difficulty:** Apprentice
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: Unprotected admin functionality with unpredictable URL](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality-with-unpredictable-url)
- **Date Solved:** 20/4/2026
## Vulnerability Summary

The app suffers from broken access control. The only defense mechanism implemented to conceal sensitive functionality is by making the admin URL unpredictable, however this unpredictability is easily locatable by public `HTML` source code of the page, allowing for vertical privilege escalation.
## Reconnaissance

Clicking on "View Page Source" to view the public HTML source code of the webpage, I see a `JavaScript` script that reads:
```javascript
var isAdmin = false; 
if (isAdmin) { 
	var topLinksTag = document.getElementsByClassName("top-links")[0]; 
	var adminPanelTag = document.createElement('a'); 
	adminPanelTag.setAttribute('href', '/admin-randomstring'); 
	adminPanelTag.innerText = 'Admin panel'; 
	topLinksTag.append(adminPanelTag); 
	var pTag = document.createElement('p'); pTag.innerText = '|'; 
	topLinksTag.appendChild(pTag); 
}
```
This basically means that if `isAdmin` is true, the page is dynamically modified to add a link labeled "Admin panel" pointing to the URL `url/admin-randomstring`. The `setAttribute` function is to set the link's destination URL, which suggests this might be the admin URL.
## Exploitation Steps

1. Access the lab. On the homepage, right click on a blank space, then select "View Page Source".
2. On the `view-source:url`, after scrolling down a bit, you should see a `JavaScript` script that reads something like this:
```javascript
var isAdmin = false; 
if (isAdmin) { 
	var topLinksTag = document.getElementsByClassName("top-links")[0]; 
	var adminPanelTag = document.createElement('a'); 
	adminPanelTag.setAttribute('href', '/admin-randomstring'); 
	adminPanelTag.innerText = 'Admin panel'; 
	topLinksTag.append(adminPanelTag); 
	var pTag = document.createElement('p'); pTag.innerText = '|'; 
	topLinksTag.appendChild(pTag); 
}
```
The random string differs from session to session.
3. Copy the `/admin-randomstring` and append it to the URL - navigate to `url/admin-randomstring`. You should see that there is an option to delete users `carlos` and `wiener`. Delete `carlos`, and the lab is solved.
## Payload Used

`/admin-randomstring`, `randomstring` found in the page source.
Sensitive functionalities are granted simply by reaching the admin URL. By finding out the hidden URL, a normal user or attacker can reach the admin URL and be granted admin's privileges.
## Root Cause

The app's only "protection" for sensitive functionality is by trying to make the admin URL unpredictable. Not only is this approach, *Security Through Obscurity*, is generally unrecommended, this unpredictability is trivially revealed through a script in the public page's source code. Other than that, no authentication or authorization checks or mechanisms are implemented to verify if it's really the intended admin browsing the admin URL or not.
## Remediation

Do not rely on security through obscurity, as hiding endpoints does not prevent from forced browsing.
- In the source code of the webapp, declare the access that is allowed for each resource and deny access by default.
- Map users to specific roles, e.g. using RBAC.
- Implement mandatory, server-side access control checks (e.g. through session tokens) on every request to a sensitive endpoint in order to verify the user's role and their privileges. Deny access if there are attempts of privilege escalation.