# -----------------------------
# Stage 1: Builder
# -----------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install --prefix=/install -r requirements.txt

# -----------------------------
# Stage 2: Runtime
# -----------------------------
FROM python:3.11-slim AS runtime

ENV TZ=UTC
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Only timezone + certs needed now
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata || true

# Python dependencies
COPY --from=builder /install /usr/local

# Application code
COPY app ./app
COPY scripts ./scripts

# Keys (required by assignment)
COPY student_private.pem ./student_private.pem
COPY student_public.pem ./student_public.pem
COPY instructor_public.pem ./instructor_public.pem

# Persistent volumes
RUN mkdir -p /data /cron \
    && chmod 0755 /data /cron

ENV SEED_FILE=/data/seed.txt
ENV PRIVATE_KEY_PATH=/app/student_private.pem

EXPOSE 8080

# -----------------------------
# Start background 2FA logger + API
# -----------------------------
CMD ["sh", "-c", "python -u scripts/cron_loop.py & exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"]

