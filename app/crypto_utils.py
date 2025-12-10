# app/crypto_utils.py
import base64
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


def load_private_key(path: str):
    """
    Load an RSA private key from a PEM file.
    """
    with open(path, "rb") as f:
        pem_data = f.read()

    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,  # we generated without password
    )
    return private_key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256.

    Args:
        encrypted_seed_b64: Base64-encoded ciphertext (from encrypted_seed.txt or API)
        private_key: RSA private key object (student_private.pem loaded)

    Returns:
        Decrypted hex seed (64-character lowercase hex string)

    Steps:
    1. Base64 decode
    2. RSA/OAEP decrypt with:
         - MGF1(SHA-256)
         - Hash SHA-256
         - Label None
    3. Decode bytes to UTF-8
    4. Validate it is 64-char lowercase hex
    5. Return seed
    """
    # 1. Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError(f"Invalid base64 for encrypted_seed: {e}")

    # 2. RSA/OAEP decrypt
    try:
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as e:
        # Important: Do NOT leak internal error details in API, just wrap it
        raise ValueError(f"RSA OAEP decryption failed: {e}")

    # 3. Decode bytes to UTF-8 string
    try:
        seed = plaintext_bytes.decode("utf-8").strip()
    except Exception as e:
        raise ValueError(f"Decrypted data is not valid UTF-8: {e}")

    # 4. Validate 64-character hex
    if len(seed) != 64:
        raise ValueError(f"Seed must be 64 characters, got {len(seed)}")

    allowed = set("0123456789abcdef")
    if any(ch not in allowed for ch in seed):
        raise ValueError("Seed must be lowercase hex (0-9, a-f)")

    # 5. Return hex seed
    return seed
