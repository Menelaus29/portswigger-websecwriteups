## Metadata

- **Difficulty:** Practitioner
- **Category:** JWT
- **Lab URL:** [Lab: JWT authentication bypass via weak signing key](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key)
- **Date Solved:** 2/10/2026
## Vulnerability Summary

The app uses a weak secret key to sign and verify tokens, which can be bruteforced using `hashcat`. This secret key, along with the header and payload structures inferred from our valid session token of the `wiener` account allow us to craft a valid token for the `administrator` account, thus gaining administrative functionalities, including the ability to delete user `carlos`.
## Reconnaissance

 - Navigate to the `/login` endpoint and login with the credentials `wiener:peter`. If you are using Burp and have the extension `JWT Editor` installed (which you should), you should see that there are requests that are highlighted - those are the requests that contain a JWT. 
- Sending the `GET /my-account?id=wiener` request to Repeater and using the `JSON Web Token` tab reveals the structure of the header and payload portions: 
![alt text](image.png)
- Modifying the `sub` field's value to `"administrator"`, copying the new token generated, then using it in the `Cookie` header while sending a request to the `/admin` endpoint results in a `401 Unauthorized` response. This means that the signature verification is active for the server's configured algorithm `HS256`.
- Modifying the `alg` field in the header to `"none"` and deleting the signature portion yields the same result `401 Unauthorized`.
- We turn our focus to the signature. The algorithm used to sign is `HS256`, a symmetric signing algorithm. This means that in order to forge a valid token, we need to know the secret key used. 
- Try bruteforcing this with `hashcat` (`hashcat -a 0 -m 16500 [JWT] path/to/wordlist`), with the [jwt-secrets wordlist](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list). The wordlist is applied against the signature calculation over `header.payload`. 
![alt text](image-1.png)
The secret key was successfully bruteforced, reveals to be `secret1`. With this secret key, we can craft a valid JWT, using the key to sign.
## Exploitation Steps

1. Navigate to the `/login` endpoint and login with credentials `wiener:peter`.
2. Intercept the `GET /my-account?id=wiener` request. Modify the payload portion of the JWT to contain these contents (base64-decoded):
```json
{  
    "iss": "portswigger",  
    "exp": [value],  
    "sub": "administrator"  
}
```
3. In the **JWT Editor** tab in Burp, add a new symmetric key:
![alt text](image-2.png)
4. Sign your modified key with this newly created symmetric key. You should receive a new JWT. Copy this value, then supply it in the `Cookie` header in the request to the `/admin` endpoint. You should receive a `200 OK`, signifying that administrative functionalities have been gained.
![alt text](image-3.png)
5.  Modify the request line to `GET /admin/delete?username=carlos HTTP/2` and send the request. `carlos` should be deleted successfully and lab is solved.
## Payload Used

`eyJraWQiOiI4YjMzNTIzZS1lZDQ5LTQ2MzgtYjkwYy1hNGIzNjkxMjdlMzUiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc5MDkxNjA0MSwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.h8QvDDixO0gzhCgLHvicXsKhVfLsZyxiBUor91EJFmQ`
The exact value changes from lab to lab, but the idea (specified in the **Reconnaissance** and **Exploitation Steps** section) is the same.

- The payload replaces `"sub": "wiener"` with `"sub": "administrator"`. Because the app maps access control directly from the `sub` claim without secondary state validation, administrative rights are granted if the token verifies. 
- The signature `h8QvDDixO0gzhCgLHvicXsKhVfLsZyxiBUor91EJFmQ` is computed as: $$\text{HMAC-SHA256}(\text{Base64URL}(Header) + "." + \text{Base64URL}(Payload), \text{"secret1"})$$ Because the server uses the identical symmetric key (`secret1`), its verification calculation matches this signature exactly, passing verification and accepting the forged payload.
## Root Cause

The app uses weak symmetric secret key (`secret1`) to sign HMAC-SHA256 tokens. Because HMAC relies on a shared symmetric key, anyone who possesses or brute-forces this key can act as a valid token issuer. Since the key space was trivial, the signature could be cracked offline without generating traffic or triggering rate limits on the application. Furthermore, the app relies entirely on client-controlled JWT claims for authorization decisions without server-side validation.
## Remediation

- For symmetric algorithms (HMAC-SHA256), use a cryptographically secure pseudorandom number generator (CSPRNG) with a key length matching/ exceeding the output size of the hash function. 
- Adopt an asymmetric algorithm such as `RS256` or `ES256`. The private signing key remains securely isolated in a Key Management Service (KMS) or backend authentication server, while consumer services only verify tokens using the public key. 
-  Store keys in environment variables or dedicated secret management services. Never hardcode them in source code or default configuration files.