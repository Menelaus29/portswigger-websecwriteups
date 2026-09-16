## Metadata

- **Difficulty:** Practitioner
- **Category:** Business logic vulnerabilities
- **Lab URL:** [Lab: Authentication bypass via flawed state machine](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine)
- **Date Solved:** 16/9/2026
## Vulnerability Summary

The app does not enforce a strict sequence of events in the authentication workflow. More specifically, it does not validate that `POST /role-selector` is made before the user can browse the page. Moreover, the app implements insecure fail-safe default to default the user's role to `administrator` . Since the app lacks server-side state tracking, this allows an attacker to intercept the `POST /login` request and drop the `GET /role-selector` that automatically comes after the login request, gaining administrative functionalities. 
## Reconnaissance

- Logging in with the credentials `wiener - peter`, we are instantly taken to `/role-selector`, where we have to select role `User` or `Content author` with a `POST /role-selector` request. Afterwards we are taken to the home page.
- Visiting the `/admin` endpoint results in a `401 Unauthorized` response that reads `Admin interface only available if logged in as an administrator`.
- Try logging in then browsing the root directory `/` (skipping the `/role-selector` screen) results in us getting logged out immediately. 
- Intercepting the `POST /role-selector` request, dropping it, then send it with the request body `role=administrator&csrf=[token]` results in a `302 Found` response. Following the redirection takes us to the website's root directory `/`, and we are logged out of our account again.
- Same process but **not** dropping the `POST /role-selector` request (try overriding the role) results in a `400 Bad Request` HTTP response that reads `"No login credentials provided"`. Omitting parameters also does not work.
-  Reaching a dead-end with bypassing the `POST /role-selector` request, we turn our focus to `GET /role-selector`. This request is made automatically right after `POST /login`. Itself does not contain any interesting (modifiable) request body (just a `csrf` parameter). 
## Exploitation Steps

1. Start intercepting with the proxy in Burp.
2. Log into your account (`wiener - peter`). Forward this request.
3. The server will automatically makes a subsequent request, `GET /role-selector`. **Drop** this request. As a result, there is no `POST /role-selector`. Then, stop the intercepting. 
4. Go to the website's root directory (`/`). Observe that you now have an "Admin panel" tab, which grants you access to the `/admin` endpoint.
5. Delete the user `carlos`. Lab is solved.
## Payload Used

Dropping the `GET /role-selector` request that the server automatically makes after `POST /login`.
Since the app does not strictly enforce the intended sequence of events in the authenticating workflow, dropping the `GET /role-selector` request that is automatically made right after `POST /login` allows us to completely bypass the role selecting process. Combined with the insecure fail-safe default implemented by the server - anyone who does not explicitly select a role is granted the `administrator` role, we can gain administrative privileges and delete the `carlos` user.
## Root Cause

The app is vulnerable due to an absence of server-side state management restricting the authentication workflow, combined with an insecure fail-safe default. Specifically, the backend logic responsible for an user's role selection is statically bound to the `GET /role-selector` endpoint. The server implicitly trusts the client's navigation sequence and fails to verify if the prerequisite state transitions (`GET /role-selector`, then `POST /role-selector`) have successfully occurred for the current session.
## Remediation

-  **Implement Server-Side State Management:** The app must track the user's progress through the authentication workflow using session variables (e.g., a session state object) or database records. 
-  **Validate State Transitions:** Before processing a request at any step, the server must verify that the session is in the correct prerequisite state. For example, before allowing the user to browse the page, the backend must verify a flag such as `session['role_selected'] == True`.
- **Drop the insecure fail-safe default**: If an user didn't select their role, the system should default to the lowest privilege level or deny access completely.
- **Enforce Strict Role Validation Prior to Authorization:** The business logic that finalizes the role selection process and, subsequently, allows the user to browse the page, must be tied to the successful completion of role-selecting, validated server-side.