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
- **Date Solved:** YYYY-MM-DD

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
#!/usr/bin/env python3
"""
Lab: [Lab Name]
Category: [e.g., SQL Injection]
Difficulty: [Apprentice/Practitioner/Expert]
Description: Exploits [vulnerability] in [parameter/endpoint]
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
    """Extract CSRF token from a page."""
    resp = session.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.find("input", {"name": "csrf"})["value"]

def exploit(target_url: str) -> None:
    session = requests.Session()
    # session.proxies = PROXY  # Uncomment to route through Burp

    print(f"[*] Target: {target_url}")

    # --- YOUR EXPLOIT LOGIC HERE ---

    print("[+] Done.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Target lab URL")
    args = parser.parse_args()
    exploit(args.url)

if __name__ == "__main__":
    main()
    
````    
Rule of thumb: **GET requests that only read data → no CSRF token needed. POST requests that submit forms → almost always need one.**
# Notes
These are things your mentor probably expects you to internalize, even if not explicitly asked:

**1. Solve manually first, always.** Never jump to scripting. If you automate something you don't understand, the writeup will be shallow and you won't learn the skill.

**2. Organize your repository well.** A clean folder structure matters:
portswigger/
├── sql-injection/
│   ├── lab-01-where-clause/
│   │   ├── writeup.md
│   │   └── exploit.py
│   └── lab-02-login-bypass/
│       ├── writeup.md
│       └── exploit.py
├── xss/
└── ...

**3. Use Burp Suite alongside your scripts.** Run your script with the proxy uncommented so you can see every request in Burp's HTTP history. This is essential for debugging and also reinforces your understanding.

**4. Track CSRF tokens properly.** Many PortSwigger labs have CSRF protection — your scripts must handle session state and token extraction, not just fire raw requests.

**5. Note what didn't work.** In your writeup, briefly mention approaches you tried that failed. Real pentest reports include dead ends — it shows methodical thinking.

**6. Difficulty ordering matters.** Don't jump to Expert labs. Go Apprentice → Practitioner → Expert within each category. The skills compound.

**7. Version control everything.** Put this on a private GitHub repo from day one. Your mentor (and future employers) can review your progress, and you build a verifiable security portfolio.

**8. Be mindful of ethics and scope.** Only run your scripts against the PortSwigger lab instances assigned to you. Never test against real sites. This is obvious, but worth internalizing as a habit early.