"""
Generate VAPID key pair for JARVIS Web Push.
Run once, paste output into .env.

    python scripts/generate_vapid.py
"""
from py_vapid import Vapid


def main():
    v = Vapid()
    v.generate_keys()

    private_pem = v.private_pem().decode().strip()
    public_key  = v.public_key

    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    import base64
    raw = public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    pub_b64 = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    print("Add these lines to your .env:\n")
    print(f"VAPID_PRIVATE_KEY={private_pem!r}")
    print(f"VAPID_PUBLIC_KEY={pub_b64}")
    print(f'VAPID_CLAIMS_SUB=mailto:johnbarber720@gmail.com')
    print("\nVAPID_PRIVATE_KEY must include the full PEM including header/footer.")
    print("Store it as a single line with \\n escapes, or use a .env multiline block.")


if __name__ == "__main__":
    main()
