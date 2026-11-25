#!/usr/bin/env python3
"""Mint token CEISACare baru tanpa 2FA → ~/.hermes/scripts/ceisacare_token.json

Endpoint /auth/login hanya butuh email (tanpa password, tanpa kode unik),
token berlaku 24 jam. Dipakai otomatis oleh update_data.py kalau token
hilang/kedaluwarsa.

Jalankan manual:
    venv\\Scripts\\python.exe refresh_token.py
"""
import base64
import datetime
import json
import os
import urllib.request

EMAIL = os.environ.get("CICA_EMAIL", "nuh.bachrudin@kemenkeu.go.id")
API = "https://apis-gw.beacukai.go.id/cica-be"
TOKEN_FILE = os.path.expanduser("~/.hermes/scripts/ceisacare_token.json")


def refresh(email=EMAIL):
    """Ambil token baru dari API, simpan ke TOKEN_FILE. Return dict token."""
    body = json.dumps({"email": email, "password": ""}).encode()
    req = urllib.request.Request(
        API + "/auth/login", data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode())
    tok = resp["token"]
    payload = tok.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    data = {
        "access_token": tok,
        "sub": claims.get("sub") or email,
        "exp": claims["exp"],
        "source": "auth/login (email-only)",
        "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=1)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except Exception:
        pass
    return data


if __name__ == "__main__":
    d = refresh()
    print("Token baru tersimpan:", TOKEN_FILE)
    print("Email :", d["sub"])
    print("Valid s/d:", datetime.datetime.fromtimestamp(d["exp"]))
