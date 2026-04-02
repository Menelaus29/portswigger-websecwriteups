# Workflow

1. Read the lab description and learning materials first
2. Solve the lab manually (understanding > speed)
3. Write the writeup while the solution is fresh
4. Then automate it with a script
5. Test the script against the lab to confirm it works

# Writeup Format
```
## Metadata

- **Difficulty:** Apprentice / Practitioner / Expert
- **Category:** e.g., SQL Injection
- **Lab URL:** https://portswigger.net/web-security/...
- **Date Solved:** DD-MM-YYYY

## Vulnerability Summary

One paragraph. What is the vulnerability, where does it exist 
in the app, and what is the impact?

## Reconnaissance

What did you observe? What requests/responses tipped you off?
Include screenshots or Burp request/response snippets here.

## Exploitation Steps

1. Navigate to...
2. Intercept the request with Burp...
3. Modify the parameter...
4. Observe that...

## Payload Used

e.g. ' OR 1=1--
Explain WHY this payload works.

## Root Cause

Why is the application vulnerable? What developer mistake 
caused this? (e.g., unsanitized input passed directly to SQL query)

## Remediation

How should a developer fix this? Be specific.
```

# Script structure
````python
"""
Lab: [Lab Name]
Category: [e.g., SQL Injection]
"""

import requests
import sys
import argparse
from bs4 import BeautifulSoup

# Disable SSL warnings for Burp proxy use

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Config
PROXY = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

def get_csrf_token(session: requests.Session, url: str) -> str:
    resp = session.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    tag = soup.find("input", {"name": "csrf"})
    if not tag or not hasattr(tag, "attrs"):
        raise ValueError("CSRF token not found")
    return str(tag["value"])
    
def exploit(target_url: str) -> None:
    session = requests.Session()
    # session.proxies = PROXY  # Uncomment to route through Burp

    print(f"Target: {target_url}")

    # --- YOUR EXPLOIT LOGIC HERE ---
    
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Target lab URL")
    args = parser.parse_args()
    exploit(args.url.rstrip("/"))
    
if __name__ == "__main__":
    main()
````    
Rule of thumb: **GET requests that only read data → no CSRF token needed. POST requests that submit forms → almost always need one.**
