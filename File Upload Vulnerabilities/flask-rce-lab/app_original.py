"""
=============================================================
  RCE Lab — Flask File Upload Vulnerability Demonstration
=============================================================
  FOR EDUCATIONAL USE ONLY.
  Run in an isolated environment (VM / container).
  Never expose this server to a public network.
=============================================================

Endpoints:
  POST /ssti       — Server-Side Template Injection via filename
  POST /pickle     — Unsafe pickle.loads() deserialization
  POST /yaml       — Unsafe yaml.load() deserialization
  POST /traversal  — Path traversal → arbitrary file overwrite
  POST /zipslip    — Zip Slip via zipfile.extractall()
  GET  /           — Browser UI (HTML)
  GET  /cheatsheet — Plain-text curl cheatsheet
"""

import os
import pickle
import zipfile
import html
import uuid
from datetime import datetime

import yaml
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR   = os.path.join(BASE_DIR, "uploads")
EXTRACT_DIR  = os.path.join(BASE_DIR, "extracted")
FLAG_DIR     = os.path.join(BASE_DIR, "flags")
LAB_IDS      = ("ssti", "pickle", "yaml", "traversal", "zipslip")
LAB_INSTANCE_ID = uuid.uuid4().hex

os.makedirs(UPLOAD_DIR,  exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

# Self-backup — used by the traversal/zipslip labs /revert endpoint
_backup = os.path.join(BASE_DIR, "app_original.py")
if not os.path.exists(_backup):
    import shutil as _shutil
    _shutil.copy2(__file__, _backup)

# Index — serves the browser UI or a plain-text curl cheatsheet
CURL_CHEATSHEET = """
╔══════════════════════════════════════════════════════════════╗
║          RCE Lab — File Upload Vulnerability Demo            ║
╚══════════════════════════════════════════════════════════════╝

All endpoints accept:  POST  multipart/form-data  field: "file"
SSTI and Traversal also accept: custom_filename (form field)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] SSTI  POST /ssti
    curl -F "file=@any.txt" -F "custom_filename={{7*7}}" \\
         http://localhost:5000/ssti

[2] Pickle  POST /pickle
    python generate_pickle.py "id"
    curl -F "file=@evil.pkl" http://localhost:5000/pickle

[3] YAML  POST /yaml
    curl -F "file=@evil.yaml" http://localhost:5000/yaml

[4] Traversal  POST /traversal
    curl -F "file=@backdoor.py" \\
         -F "custom_filename=../../app.py" \\
         http://localhost:5000/traversal

[5] Zip Slip  POST /zipslip
    python generate_zipslip.py
    curl -F "file=@evil.zip" http://localhost:5000/zipslip

Open http://localhost:5000 in a browser for the full lab UI.
Plain-text cheatsheet: http://localhost:5000/cheatsheet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


@app.route("/")
def index():
    return render_template("index.html", lab_instance_id=LAB_INSTANCE_ID)


@app.route("/cheatsheet")
def cheatsheet():
    return f"<pre>{CURL_CHEATSHEET}</pre>"


@app.after_request
def log_request(response):
    path = request.full_path.rstrip("?")
    proto = request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")
    stamp = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
    print(f'[{stamp}] "{request.method} {path} {proto}" {response.status_code} -', flush=True)
    return response


# Helper for uniform JSON response shape
def ok(output: str):
    return jsonify({"success": True,  "output": output})

def err(output: str):
    return jsonify({"success": False, "output": output}), 500


def expected_flag(lab: str):
    if lab not in LAB_IDS:
        return None

    flag_path = os.path.join(FLAG_DIR, f"{lab}.txt")
    try:
        with open(flag_path, "r", encoding="utf-8") as flag_file:
            return flag_file.read().strip()
    except FileNotFoundError:
        return None


def flag_matches(submitted: str, expected: str):
    return submitted == expected or submitted.replace("\\\\", "\\") == expected


@app.route("/submit-flag", methods=["POST"])
def submit_flag():
    data = request.get_json(silent=True) or request.form
    lab = (data.get("lab") or "").strip().lower()
    submitted = (data.get("flag") or "").strip()

    if lab not in LAB_IDS:
        return jsonify({"success": False, "message": "Unknown lab."}), 400

    flag = expected_flag(lab)
    if flag is None:
        return jsonify({"success": False, "message": "Flag file is missing."}), 500

    if not flag_matches(submitted, flag):
        return jsonify({
            "success": False,
            "lab": lab,
            "solved": False,
            "message": "Incorrect flag for this lab."
        }), 400

    return jsonify({
        "success": True,
        "lab": lab,
        "solved": True,
        "message": f"Congratulations. {lab} solved."
    })


# SSTI
@app.route("/ssti", methods=["POST"])
def ssti():
    f = request.files.get("file")
    if not f:
        return err("No file uploaded.")

    # UI sends custom_filename; curl can use f.filename as fallback
    filename = request.form.get("custom_filename") or f.filename or "unnamed"
    
    # VULNERABLE: filename is interpolated directly into the template.
    # Jinja2 evaluates {{ ... }} and {% ... %} expressions, e.g. {{7 * 7}} -> 49.
    # User-controlled input is concatenated into a template string
    # that is then evaluated by render_template_string(). 
    template = (
        "<pre>[SSTI] File received.\n\n"
        "Filename : " + filename + "\n"
        "Size     : " + str(len(f.read())) + " bytes\n"
        "</pre>"
    )

    try:
        from flask import render_template_string
        rendered = render_template_string(template)   # RCE here
        # SECURE: define a static templated with named placeholders
        # and pass user-controlled input as context variables
        # (kind of similar to SQLi protetion).
        # User data is passed through the **context parameter.
        # rendered = render_template_string(template, filename=filename, file_size=file_size)
        return ok(html.unescape(rendered))
    except Exception as e:
        return err(f"Template render error: {e}")


# Pickle — unsafe deserialization
@app.route("/pickle", methods=["POST"])
def pickle_upload():
    f = request.files.get("file")
    if not f:
        return err("No file uploaded.")

    data = f.read()
    
    # VULNERABLE: pickle.loads() blindly deserializes untrusted input.
    # __reduce__ in a crafted object runs arbitrary OS commands.
    try:
        obj = pickle.loads(data)   # RCE here
        # check_output returns bytes — decode for clean display
        display = obj.decode(errors="replace") if isinstance(obj, bytes) else obj
        return ok(f"[Pickle] Deserialized object:\n{display}")
    except Exception as e:
        return err(f"[Pickle] Deserialization error: {e}")
    # SECURE APPROACH: Never deserialize user-supplied data with pickle
    # (or other code-executing formats like marshal, shelve, or PyYAML's
    # full Loader). Use a data-only format instead (JSON, msgpack).

# YAML — unsafe deserialization
@app.route("/yaml", methods=["POST"])
def yaml_upload():
    f = request.files.get("file")
    if not f:
        return err("No file uploaded.")

    data = f.read()

    # VULNERABLE: yaml.load() with UnsafeLoader deserializes
    # Python objects via !!python/object tags.
    try:
        obj = yaml.load(data, Loader=yaml.UnsafeLoader)   # RCE here
        # SECURE: swap the Loader:
        # obj = yaml.safe_load(data)
        # check_output returns bytes — decode for clean display
        display = obj.decode(errors="replace") if isinstance(obj, bytes) else obj
        return ok(f"[YAML] Parsed object:\n{display}")
    except Exception as e:
        return err(f"[YAML] Parse error: {e}")


# Path Traversal — arbitrary file overwrite
@app.route("/traversal", methods=["POST"])
def traversal():
    f = request.files.get("file")
    if not f:
        return err("No file uploaded.")

    # UI sends custom_filename; curl can send it as a form field too
    filename = request.form.get("custom_filename") or f.filename

    if not filename:
        return err("No filename provided.")

    # VULNERABLE: os.path.join with unsanitized filename.
    # If filename cpntains traversal sequences, the join 
    # resolves OUTSIDE UPLOAD_DIR and overwrites the 
    # application source file.
    # os.path.realpath() resolves the final path but is called after
    # the dangerous join — it does not prevent the traversal but only
    # shows you where the file will actually land. The open() call that
    # follows then writes to that resolved-but-unvalidated location.
    dest     = os.path.join(UPLOAD_DIR, filename)   # traversal here
    resolved = os.path.realpath(dest)
    # SECURE: 1. use filename = secure_filename(filename) and
    # 2. verify real path stays within intended directory:
    # base     = os.path.realpath(UPLOAD_DIR)
    # dest     = os.path.join(base, safe_name)
    # resolved = os.path.realpath(dest)

    try:
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        with open(resolved, "wb") as out:
            out.write(f.read())
        return ok(
            f"[Traversal]\n"
            f"  Raw filename : {filename}\n"
            f"  Joined path  : {dest}\n"
            f"  Resolved to  : {resolved}\n"
            f"  File written : YES\n\n"
            f"If app.py was overwritten, restart the server\n"
            f"to activate the backdoor."
        )
    except Exception as e:
        return err(f"[Traversal] Write error: {e}")


# Zip Slip — directory traversal via archive extraction
@app.route("/zipslip", methods=["POST"])
def zipslip():
    f = request.files.get("file")
    if not f:
        return err("No file uploaded.")

    zip_path = os.path.join(UPLOAD_DIR, "upload.zip")
    f.save(zip_path)

    results = []

    # VULNERABLE: extractall() and manual per-entry extraction both
    # follow "../" sequences embedded in zip entry names.
    # Also exploitable via other archive formats that preserve entry
    # paths: .tar, .apk,..
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for entry in zf.namelist():
                dest     = os.path.join(EXTRACT_DIR, entry)   # no validation
                resolved = os.path.realpath(dest)
                #  SECURE: Validate every entry's resolved path against the
                # intended extract base directory BEFORE opening any file for write.
                # Reject the entire archive if any single entry would escape.

                with zf.open(entry) as src:
                    os.makedirs(os.path.dirname(resolved), exist_ok=True)
                    with open(resolved, "wb") as out:
                        out.write(src.read())

                escaped = not resolved.startswith(os.path.realpath(EXTRACT_DIR))
                flag    = "  ⚠ ESCAPED extract dir!" if escaped else ""
                results.append(f"  {entry!r:45s} → {resolved}{flag}")

        entries_report = "\n".join(results) if results else "  (empty zip)"
        return ok(
            f"[Zip Slip] Extract target: {EXTRACT_DIR}\n\n"
            f"Entries resolved:\n{entries_report}"
        )

    except zipfile.BadZipFile:
        return err("[Zip Slip] Not a valid zip file.")
    except Exception as e:
        return err(f"[Zip Slip] Extraction error: {e}")


if __name__ == "__main__":
    print(__doc__)
    app.run(debug=True, host="0.0.0.0", port=5000)
