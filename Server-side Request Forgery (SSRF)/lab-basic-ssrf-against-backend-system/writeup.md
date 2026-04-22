## Metadata

- **Difficulty:** Apprentice
- **Category:** SSRF
- **Lab URL:** [Lab: Basic SSRF against another back-end system](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-backend-system)
- **Date Solved:** 22/4/2026
## Vulnerability Summary

The app is vulnerable to **Server-side Request Forgery** (SSRF). Specifically, we can cause the app to make an HTTP request to the private IP address of its back-end systems. In order to find this IP address, we can use a bruteforce attack as there's also no defense mechanisms against brute forcing.
## Reconnaissance

Click on the "View details" button under any random item, then, at `url/product?productId=number`, intercept the `POST /product/stock` request where you click "Check stock" with Burp Suite proxy. On the intercepted request's body, there is a line that reads something like:
`stockApi=http%3A%2F%2F192.168.0.1%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D2%26storeId%3D1`
The server retrieves the stock status by passing this URL to the relevant back-end API endpoint via a front-end HTTP request.
We know the back-end system is running on a IPv4 address with prefix `192.168.0` and on port `8080`. Modifying the request to specify a private IP address: `stockApi=http://192.168.0.0:8080/admin` yields an HTTP response with a status code of `500 Internal Server Error` that, in the response body, reads:
```HTML
<p class=is-warning>
	Could not connect to external stock check service
</p>
```
This suggests that, as long as we can find `X` so that `192.168.0.X:8080` exists, we can connect to the back-end system/
## Exploitation Steps

1. Click on the "View details" button under any random item. You will be taken to `url/product?productId=[number]`.
2. Intercept the request where you click "Check stock" with Burp Suite proxy, then send it Burp Suite Intruder.
3. Needed to find the value of `X` where `192.168.0.X:8080` exists, we prepare for a brute force attack. After modifying the value of the `stockApi` field to `http://192.168.0.X:8080/admin`, selecting the payload position to be at `X`, and configuring the Payload type to be a simple list of numbers spanning from `0` to `255` with a step of 1, start a Sniper Attack in Burp Suite Intruder. 
4. After the attack's finished, sort the status code in ascending order - as we are looking for the response with a status code of `200 OK`, signifying the existence of the private IPv4 address injected. Amidst the responses with status code `500 Internal Server Error`, you shall see that there's exactly one response that has a status code of `200 OK`, where in the response message reads:
```HTML
<a href="/admin">
	Admin panel
</a>

...

<div>
	<span>
		carlos - 
	</span>
    <a href="/http://192.168.0.X:8080/admin/delete?username=carlos">
	    Delete
	</a>
</div>
```
(X is the value we intended to find). Copy the `http://192.168.0.X:8080/admin/delete?username=carlos`.
5. Inject the copied payload from Step 4 to be the value of the `stockApi` field `stockApi=http://192.168.0.X:8080/admin/delete?username=carlos`, and send the request. You should receive a `302 Found` HTTP response, signifying that a redirection has occurred. Go on the website and you should see that lab has been solved.
## Payload Used

`stockApi=http://192.168.0.X:8080/admin/delete?username=carlos`
The app fails to validate user-controllable URL before making back-end HTTP requests, allowing us to reach private non-routable IP addresses. The injected payload send a request to delete user `carlos`. 
## Root Cause

The application takes a user-controlled parameter (`stockApi`) and uses it directly to construct a backend network request without verifying if the target is intended or safe. It also implicitly trusts requests that come from the private IP address. These factors allowing for SSRF exploitation.
## Remediation

- Change the `stockApi` parameter to accept only the necessary data identifiers, such as `productId` and `storeId`. The server backend should construct the internal API request using these safe identifiers rather than trusting a client-supplied URL.
- If passing a URL is unavoidable, implement strict server-side validation using a whitelist. The application must verify that the user-supplied input exactly matches a predefined list of permitted URLs or hostnames before initiating the HTTP request. Relying on blocklisting (e.g., blocking `localhost`/`127.0.0.1`/`192.168.0.X`) is bad, as attackers can easily bypass this using alternative encodings or DNS rebinding.
- Implement egress filtering on the server. Deny all outbound traffic by default, and only permit connections to the specific internal IP addresses and ports required for the application to function.
