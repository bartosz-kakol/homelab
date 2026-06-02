FROM caddy:2.11-builder-alpine AS builder

RUN xcaddy build \
    --with github.com/bartosz-kakol/caddy-wakeonlan

FROM caddy:2.11-alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
