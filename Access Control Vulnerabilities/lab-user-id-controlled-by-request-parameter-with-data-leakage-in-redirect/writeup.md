## Metadata

- **Difficulty:** Apprentice
- **Category:** Access Control Vulnerabilities
- **Lab URL:** [Lab: User ID controlled by request parameter with data leakage in redirect](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-data-leakage-in-redirect)
- **Date Solved:** 20/5/2026

This lab is basically [Lab: User ID controlled by request parameter](../lab-user-id-controlled-by-request-parameter/writeup.md), but instead of getting access to `carlos`'s account and their API key directly on the website, you have to intercept the request to path `url/my-account?id=carlos` to get a the API key in the response that redirects us to `/login`. 