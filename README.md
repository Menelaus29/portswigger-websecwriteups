# PortSwigger WebSec Writeups

Personal writeups and Python exploit scripts documenting my preparation and learning for the [Burp Suite Certified Practitioner (BSCP)](https://portswigger.net/web-security/certification) exam through the [PortSwigger Web Security Academy](https://portswigger.net/web-security).

The goal of this repository is not only to solve each lab, but to understand the vulnerability, identify its root cause, explain why the exploit works, and document practical remediation.

> [!WARNING]
> These writeups contain full solutions and payloads. Try solving each lab yourself before reading its writeup.

## Progress

Each count represents completed writeups currently in this repository.

| Vulnerability | Apprentice | Practitioner | Expert |
| --- | :---: | :---: | :---: |
| [Access control vulnerabilities](./Access%20Control%20Vulnerabilities/) | 9/9 | 4/4 | - |
| [Authentication](./Authentication/) | 3/3 | 8/9 | 2/2 |
| [Cross-site scripting (XSS)](./Cross-site%20scripting%20%28XSS%29/) | 9/9 | 15/16 | 3/5 |
| [File upload vulnerabilities](./File%20Upload%20Vulnerabilities/) | 2/2 | 4/4 | 1/1 |
| [HTTP Host header attacks](./HTTP%20Host%20header%20attacks/) | 1/2 | 0/4 | 0/1 |
| [Path traversal](./Path%20Traversal/) | 1/1 | 5/5 | - |
| [Server-side request forgery (SSRF)](./Server-side%20Request%20Forgery%20%28SSRF%29/) | 2/2 | 3/3 | 2/2 |
| [OS Command Injection](./OS%20Command%20Injection) | 1/1 | 3/4 | - |
| [SQL injection](./SQLi/) | 2/2 | 16/16 | - |

## Repository Structure

Labs are grouped by vulnerability category. Each vulnerability's directory contains:

```text
lab-name/
|-- writeup.md    # Recon, exploitation steps, payloads, root cause, and remediation
|-- exploit.py    # Python automation for the lab, where applicable
`-- image*.png    # Supporting screenshots, where applicable
```

The full workflow and documentation formats are defined in [Workflow, writeup and script format.md](./Workflow,%20writeup%20and%20script%20format.md).

## Workflow

1. Read the lab description and supporting learning material.
2. Solve the lab manually using Burp Suite or Caido.
3. Document reconnaissance, exploitation steps, payload behavior, root cause, and remediation.
4. Automate the solution with Python where useful.
5. Test the script against a fresh lab instance.

## Tooling

- [Burp Suite](https://portswigger.net/burp) for proxying, request modification, Repeater, Intruder, and other web security testing workflows.
- [Caido](https://caido.io/) as an additional interception proxy and HTTP testing toolkit. 
- Python 3 for automating lab solutions.

The scripts commonly support routing traffic through a local interception proxy. Review each script before running it and adjust its proxy address or target-specific values as needed.

## Setup and Usage

Clone the repository, create a virtual environment, and install the Python dependencies:

```bash
python -m venv .venv
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

Start a fresh PortSwigger lab instance, then run the relevant script with its required arguments:

```bash
python path/to/exploit.py --help
```

Lab domains and session values are temporary. Some scripts may require a current lab URL, credentials, cookies, or small adjustments before use.

## Self-Made Labs

### Flask File Upload RCE Lab

The [Flask RCE lab](./File%20Upload%20Vulnerabilities/flask-rce-lab/) is a self-made vulnerable Flask application designed to explore Python-specific file upload attack paths that are not represented by PortSwigger's Apache and PHP-based file upload labs.

It contains five modules covering server-side template injection through filenames, unsafe Pickle and YAML deserialization, path traversal file overwrite, and Zip Slip. The lab includes a browser UI, progressive hints, solutions, flag validation, payload generators, and restore mechanics.

For setup instructions and full technical details, refer to the [Flask RCE lab README](./File%20Upload%20Vulnerabilities/flask-rce-lab/README.md).

## Resources

- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [Web Security Academy learning paths](https://portswigger.net/web-security/learning-paths)
- [Burp Suite Certified Practitioner](https://portswigger.net/web-security/certification)

## Acknowledgements

Special thanks to my mentors at FPT Telecom for guiding my learning!