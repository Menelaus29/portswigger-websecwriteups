## Metadata

- **Difficulty:** Apprentice
- **Category:** JWT
- **Lab URL:** [Lab: JWT authentication bypass via unverified signature](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature)
- **Date Solved:** 1/10/2026
## Vulnerability Summary

The app uses a JWT-based mechanism for handing sessions and access control, but it does not verify the signature of the JWTs it receives. This allows us to manually modify the payload in the JWT, specifically the `sub` field, thus gaining access to administrative functionalities at the `/admin` endpoint and deleting user `carlos`.
## Reconnaissance

Per the lab's description, "the server doesn't verify the signature of any JWTs that it receives". This means we can modify the base64 encoded payload portion in the JWT, specifically the field of our username `wiener` to `administrator` to gain administrative functionalities, providing that the admin's JWT follows the same format. 
- Navigate to the `/login` endpoint and login with the credentials `wiener:peter`. If you are using Burp and have the extension `JWT Editor` installed (which you should), you should see that there are requests that are highlighted - those are the requests that contain a JWT. 
- Sending the `GET /my-account?id=wiener` request to Repeater and using the `JSON Web Token` tab reveals the structure of the payload portion:
![alt text](image.png)
- Modifying the `sub` field's value to `"administrator"`, copying the new token generated, then using it in the `Cookie` header while sending a request to the `/admin` endpoint results in a `200 OK` HTTP Response reveals that we have successfully gained administrative privileges:
![alt text](image-1.png)
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
3. Copy the newly generated token and use it in the `Cookie` header while sending a request to the `admin` endpoint. You should see that you have gained administrative functionalities in the response.
4. Modify the request line to `GET /admin/delete?username=carlos HTTP/2` and send the request. `carlos` should be deleted successfully and lab is solved.
## Payload Used

Session cookie:
```
eyJraWQiOiIyOGI1MGY2OS0wZTcxLTQ3YzgtODRiMC03MzZhYzM3MGE2YmUiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc5MDg1MDI1NSwic3ViIjoiYWRtaW5pc3RyYXRvciJ9.fsDFpbF3NiDWLJj_QZPW6F134CYjhEfjlrsptpiJLa2V9ikeGRC_XTF1VB3uUtcTNIiUXNl76G4zBzu5hVL8MnkXue1Pf-n8Iz-p8Neco-UqB_FWOOnA4ub9dUE9Y1OFwXp2zxUI8f1ZGa1sP4eVdo66tmYNHFiynQYKf5yh3FSPPkICrcKbdOsQg5CiBNlRLfw6Qb3YdkVuehQVZeAVbh2q2vDcFXeNVrY5Y426HS7m7QxfXT4LwHpUr4Q3wMtWhuYteL4HfmzWYOBYV6waLOCEiZdCGqlKUk9-9psPq0x7AUqlyFtbnvU-Z-53Ud53fPiAV3FBHTr3oVRb3wk0tw
```
The exact value changes from lab to lab but the core idea is the same - the `sub` field in the payload portion has value `administrator`.
We substituted the `wiener` value of the payload portion with `administrator`. Since the server doesn't verify the signature of JWTs, this forged token is valid and grants us access to the `admin` endpoint.
## Root Cause

The server doesn't verify the signature of any JWTs that it receives, the signature portion - which is supposed to be used for upholding the integrity, authenticity, and non-repudiation properties of the token - is completely irrelevant. The app's backend presumably parses and decodes the JWT claims with `decode()` but doesn't pass the signature to a cryptographic verification method like `verify()`. Since the header and payload portions of a JWT is only encoded, one can trivially read and infer the structure of these portions, allowing them to forge a valid token. 
## Remediation

- **Enforce Cryptographic Verification Prior to Processing:**
    - Configure the backend JWT parsing library to strictly verify token signatures against the server's public key (for asymmetric algorithms like RS256) or shared secret (for symmetric algorithms like HS256) before decoding or trusting any claims.
    - Never process or deserialize claims from unverified tokens (e.g., avoid using methods like `jwt.decode(..., verify=False)` or manual base64 decoding of the payload).
- **Algorithm & Key Whitelisting:**
    - Hardcode expected signing algorithms (e.g., explicitly restrict allowed algorithms to `["RS256"]`) in the backend verification configuration to prevent algorithm-downgrade or `none`-algorithm attacks.
- **Reject Malformed or Tampered Tokens:**
    - Reject tokens with invalid signatures with an HTTP `401 Unauthorized` status and terminate the request lifecycle without executing backend authorization logic.