FROM alpine:3.18

RUN apk add --no-cache \
    g++ \
    python3 \
    py3-pip \
    bash \
    coreutils

WORKDIR /app

COPY judge.sh /app/judge.sh
RUN chmod +x /app/judge.sh

ENTRYPOINT ["/app/judge.sh"]
