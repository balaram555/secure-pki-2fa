# test_decrypt.py  (ROOT LO UNDAALI)

from app.crypto_utils import load_private_key, decrypt_seed


def main():
    # 1. Load private key from root file
    private_key = load_private_key("student_private.pem")

    # 2. Read encrypted seed from file
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed_b64 = f.read().strip()

    # 3. Decrypt
    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

    print("Decrypted hex seed:", hex_seed)
    print("Length:", len(hex_seed))


if __name__ == "__main__":
    main()
