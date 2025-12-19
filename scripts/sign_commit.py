#!/usr/bin/env python3
# scripts/sign_commit.py
"""
Sign latest git commit hash with RSA-PSS (SHA-256), then encrypt the signature
with instructor public key using RSA-OAEP (SHA-256). Output:
- Commit Hash (40 hex chars)
- Encrypted Signature (base64, single line)
"""

import argparse
import base64
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

def get_latest_commit_hash():
    p = subprocess.run(["git", "log", "-1", "--format=%H"], capture_output=True, text=True, check=True)
    h = p.stdout.strip()
    if len(h) != 40:
        raise ValueError(f"Commit hash looks wrong: '{h}'")
    return h

def load_private_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_private_key(data, password=None, backend=default_backend())

def load_public_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_public_key(data, backend=default_backend())

def sign_message(message: str, private_key: rsa.RSAPrivateKey) -> bytes:
    msg = message.encode("utf-8")  # sign ASCII/UTF-8 bytes of commit hash
    signature = private_key.sign(
        msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def main():
    parser = argparse.ArgumentParser(description="Sign latest git commit and encrypt signature.")
    parser.add_argument("--private", "-k", required=True, help="Path to student_private.pem")
    parser.add_argument("--instructor", "-i", required=True, help="Path to instructor_public.pem")
    parser.add_argument("--commit", "-c", required=False, help="Optional commit hash to sign (40 hex chars)")
    args = parser.parse_args()

    priv_path = Path(args.private)
    instr_path = Path(args.instructor)
    if not priv_path.exists():
        raise FileNotFoundError(f"Private key file not found: {priv_path}")
    if not instr_path.exists():
        raise FileNotFoundError(f"Instructor public key file not found: {instr_path}")

    commit_hash = args.commit if args.commit else get_latest_commit_hash()
    if len(commit_hash) != 40:
        raise ValueError("Commit hash must be 40 hex characters.")

    private_key = load_private_key(priv_path)
    instructor_pub = load_public_key(instr_path)

    signature = sign_message(commit_hash, private_key)
    encrypted = encrypt_with_public_key(signature, instructor_pub)
    enc_b64 = base64.b64encode(encrypted).decode("utf-8")

    print("Commit Hash:")
    print(commit_hash)
    print()
    print("Encrypted Commit Signature (BASE64, single line):")
    print(enc_b64)
    print()
    print("NOTE: Copy the above base64 string as a single line into the submission form.")
    return 0

if __name__ == "__main__":
    main()
