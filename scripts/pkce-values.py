#!/usr/bin/env python3
import base64
import hashlib
import secrets

verifier = secrets.token_urlsafe(64)
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b"=").decode()

print("code_verifier:", verifier)
print("code_challenge:", challenge)
print("state:", secrets.token_urlsafe(24))
print("nonce:", secrets.token_urlsafe(24))
