# app/main.py

import os
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.crypto_utils import load_private_key, decrypt_seed
from app.totp_utils import generate_totp_code, seconds_remaining, verify_totp_code

app = FastAPI()

# Environment-based config (useful for Docker later)
SEED_FILE = os.environ.get("SEED_FILE", "/data/seed.txt")
PRIVATE_KEY_PATH = os.environ.get("PRIVATE_KEY_PATH", "student_private.pem")


# ---------- Request Models ----------

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: str | None = None


# ---------- Health Check (optional but useful) ----------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Endpoint 1: POST /decrypt-seed ----------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    """
    Accepts base64-encoded encrypted_seed, decrypts it using
    RSA/OAEP-SHA256 with student private key, validates 64-char hex,
    and stores it in /data/seed.txt.
    """
    # 1) Load private key
    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
    except Exception as e:
        # Don't expose internal error to client
        print("Failed to load private key:", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Decryption failed"},
        )

    # 2) Decrypt seed
    try:
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)
    except Exception as e:
        print("Decryption error:", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Decryption failed"},
        )

    # 3) Store seed at /data/seed.txt
    try:
        os.makedirs(os.path.dirname(SEED_FILE), exist_ok=True)
        with open(SEED_FILE, "w") as f:
            f.write(hex_seed)
    except Exception as e:
        print("Failed to save seed:", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Decryption failed"},
        )

    # 4) Success
    return {"status": "ok"}


# ---------- Endpoint 2: GET /generate-2fa ----------

@app.get("/generate-2fa")
def generate_2fa():
    """
    Reads seed from persistent storage (/data/seed.txt),
    generates current TOTP code, and returns remaining validity seconds.
    """
    # 1) Check if seed exists
    if not os.path.exists(SEED_FILE):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    # 2) Read hex seed
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
    except Exception as e:
        print("Failed to read seed:", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    # 3) Generate TOTP code and remaining seconds
    try:
        code = generate_totp_code(hex_seed)
        valid_for = seconds_remaining()
    except Exception as e:
        print("TOTP generation error:", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    # 4) Success
    return {"code": code, "valid_for": valid_for}


# ---------- Endpoint 3: POST /verify-2fa ----------

@app.post("/verify-2fa")
def verify_2fa(body: Verify2FARequest):
    """
    Accepts {"code": "123456"}, verifies against stored seed
    with ±1 period (±30s) tolerance.
    """
    # 1) Validate code present
    if body.code is None or body.code.strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Missing code"},
        )

    code = body.code.strip()

    # 2) Check if seed exists
    if not os.path.exists(SEED_FILE):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    # 3) Read hex seed
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
    except Exception as e:
        print("Failed to read seed:", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    # 4) Verify code with ±1 period tolerance
    try:
        is_valid = verify_totp_code(hex_seed, code, valid_window=1)
    except Exception as e:
        print("Verification error:", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    # 5) Always 200 OK, with valid: true/false
    return {"valid": is_valid}
