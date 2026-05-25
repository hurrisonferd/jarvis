"""
Generate VAPID key pair for JARVIS Web Push.
Run once, paste output into .env.

    python scripts/generate_vapid.py
"""
import subprocess
import base64


def main():
    ec_pem = subprocess.run(
        ['openssl', 'ecparam', '-name', 'prime256v1', '-genkey', '-noout'],
        capture_output=True, check=True
    ).stdout.decode()

    pub_der = subprocess.run(
        ['openssl', 'ec', '-pubout', '-outform', 'DER'],
        input=ec_pem.encode(), capture_output=True, check=True
    ).stdout
    pub_b64 = base64.urlsafe_b64encode(pub_der[-65:]).rstrip(b'=').decode()

    priv_der = subprocess.run(
        ['openssl', 'ec', '-outform', 'DER'],
        input=ec_pem.encode(), capture_output=True, check=True
    ).stdout
    idx = priv_der.index(b'\x04\x20') + 2
    priv_b64 = base64.urlsafe_b64encode(priv_der[idx:idx+32]).rstrip(b'=').decode()

    print("Add these lines to your .env:\n")
    print(f"VAPID_PUBLIC_KEY={pub_b64}")
    print(f"VAPID_PRIVATE_KEY={priv_b64}")
    print(f"VAPID_CLAIMS_SUB=mailto:johnbarber720@gmail.com")
    print("\nIf you regenerate these keys, update VAPID_PUBLIC_KEY in docs/index.html too.")


if __name__ == "__main__":
    main()
