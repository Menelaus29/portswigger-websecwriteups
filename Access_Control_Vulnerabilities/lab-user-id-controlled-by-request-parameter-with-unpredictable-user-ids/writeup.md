## Metadata

- **Difficulty:** Apprentice
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: User ID controlled by request parameter, with unpredictable user IDs](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-unpredictable-user-ids)
- **Date Solved:** 21/4/2026
## Vulnerability Summary

The app uses globally unique identifiers (GUID) to identify users, allowing them to access their page using an URL like: `url/my-account?id=userguid`. However, the GUIDs that belong to other users are disclosed on the webpage. The app does not implement any checks regarding the identity of the user accessing a GUID, leading to a **Insecure Direct Object Reference** (IDOR) vulnerability which allows horizontal privilege escalation.
## Reconnaissance

After logging in with the credentials `wiener - peter` (provided by the lab), intercept the request to reload the "My account" page (URL `url/my-account?id=wienerguid`). The server seems to rely entirely on the `id` parameter and there's no visible validation if the provided session cookie actually belongs to the user ID being requested. This signifies that IDOR is present, thus horizonal privilege escalation is possible.
## Exploitation Steps

1. Navigate to `url/login` and login with the credentials `wiener-peter`.
2. Intercept the request to reload the "My account" page (URL `url/my-account?id=wienerguid`).
3. On the website, click on "Home". Click on "View post" on posts until you see one that is written by user `carlos`.
4. View `carlos` profile by clicking on the name of the post's author. You should be taken to `carlos` blog page at URL `url/blogs?userId=carlosguid`. Copy this GUID string of `carlos`.
5. On the intercepted request on Step 2, modify the request path to `GET /my-account?id=carlosguid` then send the request. The HTTP response should have a status code of `200 OK` and a response message that reads: 
```
<p>
	Your username is: carlos
</p>
<div>
	Your API Key is: carlosapikey
</div>
```
Copy the value of the `Your API Key is:` field the submit the solution on the website. You should see that lab is solved.
## Payload Used

`/my-account?id=carlosguid`.
Modifying the GUID to another user grants access to that user even if their login credentials are unknown. 
## Root Cause

The app implements an unpredictable GUID to verify users. However, these GUIDs are not hidden, and the application implicitly trusts client-side provided state without server-side validation or cryptographic integrity, thus allowing us to access other users' account simply by modifying the value of the GUID field.
## Remediation

- When rendering the "My Account" page or returning sensitive data, the application should drop the `id` parameter entirely from the request. Instead, it should extract the user's identity directly from the authenticated session object (e.g., the server-side session store mapped to the user's session cookie) and fetch the corresponding data.
- If passing the user ID via a parameter is strictly required by the application's architecture, the backend must explicitly verify authorization before returning data. The server must check if the ID of the currently authenticated user (derived from their session token) matches the ID supplied in the request parameter. If they do not match, the application must return an `HTTP 403 Forbidden` or `HTTP 401 Unauthorized` response.
- Relying on the unpredictability of a GUID is *Security through obscurity*. GUIDs should be treated as public identifiers, and authorization must always be enforced programmatically at the data-access layer.
