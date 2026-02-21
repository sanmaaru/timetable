FROM ubuntu:22.04

# ===== 1. 시스템 설정 =====
RUN apt-get update && apt-get install -y ca-certificates tar \
    && rm -rf /var/lib/apt/lists/*

# ===== 2. UV 설치 (사내망 우회) =====
COPY uv-x86_64-unknown-linux-gnu.tar.gz /tmp/
RUN tar -xzf /tmp/uv-x86_64-unknown-linux-gnu.tar.gz -C /tmp \
    && mv /tmp/uv-x86_64-unknown-linux-gnu/uv /usr/local/bin/uv \
    && chmod +x /usr/local/bin/uv \
    && rm -rf /tmp/*
RUN rm -f uv-x86_64-unknown-linux-gnu.tar.gz

# ===== 3. 프로젝트 설정 및 패키지 설치 =====
WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 5000

CMD ["uv", "run", "uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000"]