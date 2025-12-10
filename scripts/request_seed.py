# scripts/request_seed.py
import json
import requests

INSTRUCTOR_API = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"


def request_seed(student_id: str, github_repo_url: str, api_url: str = INSTRUCTOR_API):
    """
    Request encrypted seed from instructor API and save it to encrypted_seed.txt
    """

    # 1. Read student public key from PEM file
    with open("student_public.pem", "r") as f:
        public_key_pem = f.read()

    # 2. Prepare HTTP POST payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem,
    }

    headers = {
        "Content-Type": "application/json"
    }

    # 3. Send POST request
    resp = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=30)

    # Raise error if HTTP-level failure
    resp.raise_for_status()

    # 4. Parse JSON response
    data = resp.json()
    print("API response:", data)

    if data.get("status") != "success":
        raise RuntimeError(f"API returned error: {data}")

    encrypted_seed = data["encrypted_seed"]

    # 5. Save encrypted seed to file (DO NOT COMMIT THIS)
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("✅ Encrypted seed saved to encrypted_seed.txt")


if __name__ == "__main__":
    # TODO: fill these with your real values
    STUDENT_ID = "22A91A0599"
    GITHUB_REPO_URL = "https://github.com/balaram555/secure-pki-2fa"

    request_seed(STUDENT_ID, GITHUB_REPO_URL)
