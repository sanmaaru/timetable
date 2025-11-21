FROM ubuntu:22.04

# ===== Environment Setting =====
RUN apt update && apt install -y wget ca-certificates tar \
     && rm -rf /var/lib/apt/lists/*

COPY uv-x86_64-unknown-linux-gnu.tar.gz /tmp/uv.tar.gz
RUN mkdir -p /tmp/uv-extract \
    && tar -xzf /tmp/uv.tar.gz -C /tmp/uv-extract \
    && mv /tmp/uv-extract/uv-x86_64-unknown-linux-gnu/uv /usr/local/bin/uv \
    && chmod 777 /usr/local/bin/uv \
    && rm -rf /tmp/uv.tar.gz /tmp/uv-extract

RUN uv --version

# ===== Project Settings =====
WORKDIR /app
COPY ./ /app
RUN rm -f uv-x86_64-unknown-linux-gnu.tar.gz

RUN uv sync

EXPOSE 5000