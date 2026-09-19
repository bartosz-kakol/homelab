FROM ubuntu:24.04

ARG VSCODE_CLI_ARCH=linux-x64
ARG TARGETARCH

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        libatomic1 \
        tar \
	gosu \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash coder

RUN set -eux; \
    case "${TARGETARCH:-amd64}" in \
        amd64) CLI_ARCH="cli-linux-x64" ;; \
        arm64) CLI_ARCH="cli-linux-arm64" ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac; \
    curl -Lk "https://update.code.visualstudio.com/latest/${CLI_ARCH}/stable" -o /tmp/vscode_cli.tar.gz; \
    tar -xf /tmp/vscode_cli.tar.gz -C /usr/local/bin; \
    rm /tmp/vscode_cli.tar.gz; \
    chmod +x /usr/local/bin/code

RUN mkdir -p /home/coder/.vscode-server-data /home/coder/projects && \
    chown -R coder:coder /home/coder

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

#USER coder
WORKDIR /home/coder/projects

VOLUME ["/home/coder/.vscode-server-data", "/home/coder/projects"]

ENTRYPOINT ["/entrypoint.sh"]
