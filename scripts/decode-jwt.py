#!/usr/bin/env python3
import base64
import json
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: decode-jwt.py <jwt>")

parts = sys.argv[1].split(".")
if len(parts) != 3:
    raise SystemExit("not a three-part JWT")

for label, segment in [("HEADER", parts[0]), ("PAYLOAD", parts[1])]:
    segment += "=" * (-len(segment) % 4)
    print(f"\n{label}\n------")
    print(json.dumps(json.loads(base64.urlsafe_b64decode(segment)), indent=2))

print("\nNOTE: decoding is not signature validation.")
