FROM alpine:3.18

RUN apk add --no-cache \
    g++ \
    python3 \
    py3-pip \
    bash \
    coreutils

WORKDIR /sandbox

COPY judge.sh /sandbox/judge.sh
RUN chmod +x /sandbox/judge.sh

ENTRYPOINT ["/sandbox/judge.sh"]
