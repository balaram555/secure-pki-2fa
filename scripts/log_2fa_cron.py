#!/usr/bin/env python3
# scripts/log_2fa_cron.py
import os
from datetime import datetime, timezone
from app.totp_utils import generate_totp_code

SEED_PATH = "/data/seed.txt"
LOG_PATH = "/cron/last_code.txt"

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def main():
    try:
        if not os.path.exists(SEED_PATH):
            print(f"{now_utc()} - ERROR: seed file not found", flush=True)
            return
        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()
        if not hex_seed:
            print(f"{now_utc()} - ERROR: seed empty", flush=True)
            return
        code = generate_totp_code(hex_seed)
        print(f"{now_utc()} - 2FA Code: {code}", flush=True)
    except Exception as e:
        print(f"{now_utc()} - ERROR: {e}", flush=True)

if __name__ == "__main__":
    main()
