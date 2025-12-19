import sys
sys.path.insert(0, "/app")   # ✅ MUST be first

import time
import os
from datetime import datetime, timezone
from app.totp import generate_totp_code

LOG_FILE = "/cron/last_code.txt"
SEED_FILE = "/data/seed.txt"

# 🔥 PROOF: create file immediately on startup
with open(LOG_FILE, "a") as f:
    f.write("STARTED background logger\n")

while True:
    try:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists(SEED_FILE):
            with open(SEED_FILE, "r") as f:
                hex_seed = f.read().strip()
            code = generate_totp_code(hex_seed)
            line = f"{ts} - 2FA Code: {code}\n"
        else:
            line = f"{ts} - waiting for seed\n"

        with open(LOG_FILE, "a") as f:
            f.write(line)

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"ERROR: {e}\n")

    time.sleep(60)
