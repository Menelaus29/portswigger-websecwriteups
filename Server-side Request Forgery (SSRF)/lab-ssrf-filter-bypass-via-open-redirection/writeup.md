## Metadata

- **Difficulty:** Practitioner
- **Category:** SSRF
- **Lab URL:** [Lab: SSRF with filter bypass via open redirection vulnerability](https://portswigger.net/web-security/ssrf/lab-ssrf-filter-bypass-via-open-redirection)
- **Date Solved:** 11/08/2026
## Vulnerability Summary

The app is vulnerable to Server-side Request Forgery (SSRF) in the stock checking functionality. Specifically, an attacker can exploit a legitimate open redirection endpoint to supply a URL in the `stockApi` parameter in the request made by the server in the process of stock checking for the server to redirect to the `/admin` endpoint from the local machine, which the app implicitly trusts. 
## Reconnaissance

- Click on the "View details" button under any random item, then, at `url/product?productId=number`, intercept the `POST /product/stock` request where you click "Check stock" with Burp Suite proxy/Caido. In the request (sent by the server), you should see something like:
```
stockApi=%2Fproduct%2Fstock%2Fcheck%3FproductId%3D2%26storeId%3D1
```
which is the URL-encoded version of:
```
stockApi=/product/stock/check?productId=2&storeId=1
```
- Try changing the value of this `stockApi` parameter directly to: `http://192.168.0.12:8080/admin` will result in a `400 Bad Request` HTTP Response that reads: 
```
"Invalid external stock check url 'Invalid URL'"
```
URL-encoding the payload does not help either. As the lab's description said, "The stock checker has been restricted to only access the local application, so you will need to find an open redirect affecting the application first."
- Under each product's page, there's a "Next Product" button. Clicking this button produces this request:
```
GET /product/nextProduct?currentProductId=2&path=/product?productId=3 HTTP/1.1
```
This is the open redirection we are looking for. This button redirects the current product page to the next one, which is controlled by the user-suppliable `path` parameter.
## Exploitation Steps

1. Click on the "View details" button under any random item. You will be taken to `url/product?productId=[number]`.
2. Intercept the request where you click "Check stock" with Burp Suite proxy, then send it to Burp Suite Repeater.
3. Modify the value of the `stockApi` field to `%2Fproduct%2FnextProduct%3FcurrentProductId%3D2%26path%3Dhttp%3A%2F%2F192.168.0.12%3A8080%2Fadmin%2Fdelete%3Fusername%3Dcarlos`, then send the request.
4. Observe that you receive a `200 OK` HTTP Response that reads "User deleted successfully!" with only the user `wiener` left. Go on to the website, and you should see that lab is solved.
## Payload Used

`%2Fproduct%2FnextProduct%3FcurrentProductId%3D2%26path%3Dhttp%3A%2F%2F192.168.0.12%3A8080%2Fadmin%2Fdelete%3Fusername%3Dcarlos`
This is the URL-encoded version of:
```

/product/nextProduct?currentProductId=2&path=http://192.168.0.12:8080/admin/delete?username=carlos
```
 We use the open redirection endpoint of `/nextProduct` and modify the parameter `path` to change where it redirects to.
## Root Cause

The vulnerability stems from two distinct developer errors combined into a chain:
1. **Unsafe Redirect Handling (SSRF):** The backend HTTP client responsible for fetching the `stockApi` URL is configured to automatically follow HTTP redirects blindly. It validates the initial URL against a strict whitelist or regex (ensuring it targets the local application) but fails to apply the same validation to the redirect target.
2. **Unvalidated Input (Open Redirection):** The `/product/nextProduct` endpoint takes user-supplied input via the `path` parameter and reflects it directly into the `Location` header of the HTTP response without verifying if the destination is a safe, internal relative path.
## Remediation

- Disable auto-following of HTTP redirects in the backend HTTP client used for the stock check. If the application strictly requires following redirects, the backend must intercept the redirect and recursively validate every new `Location` URL against a whitelist before issuing the subsequent request.
- Do not allow arbitrary or absolute URLs in the `path` parameter. Enforce strict server-side validation to ensure the input is only a relative path (e.g., regex matching `^/product\?productId=[0-9]+$`). Alternatively, map product IDs to user session flow and remove the user-controllable `path` parameter entirely.