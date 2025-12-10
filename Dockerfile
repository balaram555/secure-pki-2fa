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
WORKDIR /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata || true

COPY --from=builder /install /usr/local

COPY app ./app
COPY scripts ./scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron

COPY student_private.pem ./student_private.pem
COPY student_public.pem ./student_public.pem
COPY instructor_public.pem ./instructor_public.pem

RUN mkdir -p /data /cron \
    && chmod 0755 /data /cron

RUN chmod 0644 /etc/cron.d/2fa-cron \
    && crontab /etc/cron.d/2fa-cron

EXPOSE 8080

ENV SEED_FILE=/data/seed.txt
ENV PRIVATE_KEY_PATH=/app/student_private.pem
ENV PYTHONUNBUFFERED=1

CMD [ "sh", "-c", "service cron start || cron && exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8080" ]
