import base64
import pyotp

def generate_totp_code(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()
