# test_decrypt_standalone.py
# Standalone test: NO imports from app, just directly use cryptography

import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes


def load_private_key(path: str):
    with open(path, "rb") as f:
        pem_data = f.read()
    return serialization.load_pem_private_key(pem_data, password=None)


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    ciphertext = base64.b64decode(encrypted_seed_b64)

    plaintext_bytes = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    seed = plaintext_bytes.decode("utf-8").strip()

    if len(seed) != 64:
        raise ValueError(f"Seed must be 64 characters, got {len(seed)}")

    allowed = set("0123456789abcdef")
    if any(ch not in allowed for ch in seed):
        raise ValueError("Seed must be lowercase hex")

    return seed


if __name__ == "__main__":
    # 1) Load your private key
    priv_key = load_private_key("student_private.pem")

    # 2) Read encrypted_seed from file
    with open("encrypted_seed.txt", "r") as f:
        enc_b64 = f.read().strip()

    # 3) Decrypt
    hex_seed = decrypt_seed(enc_b64, priv_key)

    print("Decrypted hex seed:", hex_seed)
    print("Length:", len(hex_seed))
