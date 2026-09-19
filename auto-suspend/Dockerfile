FROM debian:bookworm-slim

ARG VERSION="1.0"

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN wget -O auto-suspend https://github.com/bartosz-kakol/auto-suspend/releases/download/v${VERSION}/auto-suspend_linux_amd64 && \
    chmod +x auto-suspend

ENTRYPOINT ["./auto-suspend", "run", "--remote", "config.yaml"]
