#!/usr/bin/env python3
"""Generate VAPID key pair for Web Push. Run once, paste output into .env."""
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()

pub_numbers = public_key.public_numbers()
x = pub_numbers.x.to_bytes(32, "big")
y = pub_numbers.y.to_bytes(32, "big")
pub_b64 = base64.urlsafe_b64encode(b"\x04" + x + y).rstrip(b"=").decode()

priv_value = private_key.private_numbers().private_value.to_bytes(32, "big")
priv_b64 = base64.urlsafe_b64encode(priv_value).rstrip(b"=").decode()

print("# Paste these three lines into your .env file")
print(f"VAPID_PRIVATE_KEY={priv_b64}")
print(f"VAPID_PUBLIC_KEY={pub_b64}")
print("VAPID_CLAIMS_SUB=mailto:johnbarber720@gmail.com")
