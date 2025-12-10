# app/totp_utils.py
import base64
import time

import pyotp


def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to base32 string for TOTP.
    """
    # 1) hex -> bytes
    seed_bytes = bytes.fromhex(hex_seed)
    # 2) bytes -> base32 (string)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed.

    TOTP config:
    - Algorithm: SHA-1 (default in pyotp)
    - Period: 30 seconds
    - Digits: 6
    """
    # 1 & 2) hex -> bytes -> base32 string
    base32_seed = hex_to_base32(hex_seed)

    # 3) Create TOTP object
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)  # SHA-1 default

    # 4) Generate current 6-digit code
    code = totp.now()

    # 5) Return code
    return code


def seconds_remaining(period: int = 30) -> int:
    """
    Return how many seconds left in current TOTP period (0–29).
    """
    now = int(time.time())
    return period - (now % period)


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance.

    - valid_window=1 means accept current, previous, and next 30s window (±30s).
    """
    # 1) Convert hex -> base32
    base32_seed = hex_to_base32(hex_seed)

    # 2) Create TOTP object
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)

    # 3) Verify with time window tolerance
    is_valid = totp.verify(code, valid_window=valid_window)

    # 4) Return result
    return is_valid
