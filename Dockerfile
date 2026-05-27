FROM alpine:3.23 AS downloader

ARG PROM_VERSION

# hadolint ignore=DL3018
RUN apk add --no-cache wget tar

RUN wget -q https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz && \
    tar xzf prometheus-${PROM_VERSION}.linux-amd64.tar.gz

FROM python:3.14-alpine3.23

ARG PROM_VERSION

ENV PROM_VERSION=${PROM_VERSION}

RUN adduser \
    -h /home/promtools \
    -g "App User" \
    -s /sbin/nologin \
    -D \
    -u 1000 \
    promtools \
  && mkdir /data \
  && chown promtools:promtools /data

COPY --chown=root:root --from=downloader \
    /prometheus-${PROM_VERSION}.linux-amd64/prometheus \
    /usr/local/bin/prometheus

COPY --chown=root:root --from=downloader \
    /prometheus-${PROM_VERSION}.linux-amd64/promtool \
    /usr/local/bin/promtool

COPY --chown=root:root --from=downloader \
    /prometheus-${PROM_VERSION}.linux-amd64/prometheus.yml \
    /etc/prometheus/prometheus.yml

RUN mkdir -p /var/lib/prometheus && \
    chown -R promtools:promtools /var/lib/prometheus /etc/prometheus

COPY --chmod=755 --chown=root:root prom2logs.py /usr/local/bin/prom2logs.py

# Copy custom config file
COPY --chown=promtools:promtools prometheus.yml /etc/prometheus/prometheus.yml

# Copy custom entrypoint script
COPY --chmod=755 entrypoint.sh /entrypoint.sh

# Copy custom generate_targets.sh script
COPY --chmod=755 generate_targets.sh /generate_targets.sh

USER promtools
