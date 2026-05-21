#!/bin/sh

set -e

# Generate the list of targets dynamically
/generate_targets.sh

# Start Prometheus
exec /usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml
