## Metadata

- **Difficulty:** Practitioner
- **Category:** SSRF
- **Lab URL:** [Lab: SSRF with blacklist-based input filter](https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter)
- **Date Solved:** 10/8/2026
## Vulnerability Summary

The app is vulnerable to Server-side Request Forgery (SSRF) in the stock checking functionality. Specifically, an attacker can supply a URL in the `stockApi` parameter in the request made by the server in the process of stock checking for the server to make a request to the `/admin` endpoint from the local machine, which the app implicitly trusts. Though there are some SSRF defenses in place, these mechanisms are weak and can be easily bypassed with case variation. 
## Reconnaissance

- Click on the "View details" button under any random item, then, at `url/product?productId=number`, intercept the `POST /product/stock` request where you click "Check stock" with Burp Suite proxy/Caido. In the request (sent by the server), you should see something like:
```html
stockApi=http%3A%2F%2Fstock.weliketoshop.net%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D4%26storeId%3D1
```
which is the URL encoded version of:
```
http://stock.weliketoshop.net:8080/product/stock/check?productId=4&storeId=1
```
- Try changing the value of this `stockApi` parameter directly to: `http://localhost/admin` will result in a `400 Bad Request` HTTP Response that reads: 
```
"External stock check blocked for security reasons"
```
- Same thing happened when `http://127.0.0.1/admin` is sent.
Since the name of the lab is `blacklist-filter`, we can assume that the underlying mechanism is blocking common sensitive hostnames and endpoints through a blacklist. We need to find a way to bypass this. I noticed that the routing framework processes paths case-insensitively (`\login` and `\LOGin` are the same).  
## Exploitation Steps

1. Click on the "View details" button under any random item. You will be taken to `url/product?productId=[number]`.
2. Intercept the request where you click "Check stock" with Burp Suite proxy, then send it to Burp Suite Repeater.
3. Modify the value of the `stockApi` field to `http://LoCaLhOsT/Admin/delete?username=carlos`, then send the request.
4. Observe that you receive a `302 Found` HTTP Response that signifies a redirection. Go on to the website. You should see that lab is solved.
## Payload Used

`http://LoCaLhOsT/Admin/delete?username=carlos`
The app's implemented blocklist is case-sensitive. It blocks `localhost` and `admin` but does not block `LoCaLhOsT` and `Admin`, which resolves to the same path.
## Root Cause

The app takes a user-controlled parameter (`stockApi`) and uses it directly to construct a backend network request without verifying if the target is intended or safe. It also implicitly trusts requests that come from the local machine, and relies on an insecure blocklist as defense against SSRF.
## Remediation

-  Change the `stockApi` parameter to accept only the necessary data identifiers, such as `productId` and `storeId`. The server backend should construct the internal API request using these safe identifiers rather than trusting a client-supplied URL.
- If passing a URL is unavoidable, implement strict server-side validation using a whitelist, **not** a blocklist. The application must verify that the user-supplied input exactly matches a predefined list of permitted URLs or hostnames before initiating the HTTP request. Relying on blocklisting is bad, as we have multiple ways to bypass this: alternatives IP representation, register a different domain name that resolves to `localhost`, or case variation as used in this lab.
- Implement egress filtering on the server. Deny all outbound traffic by default, and only permit connections to the specific internal IP addresses and ports required for the application to function.