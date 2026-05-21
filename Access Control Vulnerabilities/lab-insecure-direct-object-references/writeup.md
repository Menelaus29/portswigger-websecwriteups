## Metadata

- **Difficulty:** Practitioner
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: Insecure direct object references](https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references)
- **Date Solved:** 20/5/2026
## Vulnerability Summary

The app is vulnerable to Broken Access Control, specifically IDOR (Insecure Object Direct Reference). It stores user chat logs directly on the server's file system, and retrieves them using static URLs. However, it does not check if the requesting user is authorized to access certain referenced chat logs. Thus, we can access some chat logs that we are not meant to and retrieve sensitive information (`carlos`'s password).
## Reconnaissance

Downloading the chat logs ("View transcript") yields a HTTP Request with the header `GET /download-transcript/2.txt`. Subsequently, every request to download chat logs is made with the header `GET /download-transcript/n.txt`, n is incremented by 1 starting from 2. This suggests that we can access any transcript by replacing n with another number.
## Exploitation Steps

1. Navigate to `url/chat`. Click on "View transcript" to download chat logs.
2. On your HTTP requests history (in Burp Suite/Caido), look for 2 requests with the header `GET /download-transcript/n.txt`. `n` can be any number starting from 2.
![alt text](image.png)
3. Modify the HTTP header to `GET /download-transcript/1.txt HTTP/1.1` and send the request. You should get a `200 OK` HTTP Response that, in the response body, reads:
```
CONNECTED: -- Now chatting with Hal Pline --
You: Hi Hal, I think I've forgotten my password and need confirmation that I've got the right one
Hal Pline: Sure, no problem, you seem like a nice guy. Just tell me your password and I'll confirm whether it's correct or not.
You: Wow you're so nice, thanks. I've heard from other people that you can be a right ****
Hal Pline: Takes one to know one
You: Ok so my password is password_string. Is that right?
Hal Pline: Yes it is!
You: Ok thanks, bye!
Hal Pline: Do one!
```
`password_string` is a random value that differs from session to session. Copy this `password_string` value and log in with it and username `carlos`. You should be logged in, and lab is solved.
## Payload Used

`GET /download-transcript/1.txt HTTP/1.1`
This is a simple HTTP request to download the chat logs file named `1.txt`.
## Root Cause

The app used user-supplied input to access objects directly. This means that we can modify this input (in this case to `1.txt`) to obtain unauthorized access to chat logs that belong to another user.
## Remediation

- Enable server-side authorization checks. Every request that accesses an object must verify that the authenticated user has permissions to access that specific object
- Validate access rights at application logic or data layer
- Use unpredictable UUIDs to identify resources (users, files...) to prevent enumeration attempts and information leaking.
