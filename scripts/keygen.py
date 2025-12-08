# scripts/keygen.py
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair (private + public) as PEM files.
    - Key size: 4096 bits
    - Public exponent: 65537
    """

    # 1. Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # 2. Extract public key
    public_key = private_key.public_key()

    # 3. Serialize private key to PEM (no password)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # 4. Serialize public key to PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # 5. Save both files to repo root
    with open("student_private.pem", "wb") as f:
        f.write(private_pem)

    with open("student_public.pem", "wb") as f:
        f.write(public_pem)

    print("✅ RSA 4096-bit key pair generated:")
    print(" - student_private.pem")
    print(" - student_public.pem")


if __name__ == "__main__":
    generate_rsa_keypair()
