#!/bin/sh
set -e

# Defaults or environment overrides
RANGE="${ADDRESS_RANGE:-10.86.0}"
RANGE_START="${START:-4}"
RANGE_END="${END:-30}"
PORT_START="${PORT_START:-8000}"
PORT_END="${PORT_END:-8002}"
OUTFILE="${OUTFILE:-/etc/prometheus/targets.json}"

echo "Generating hosts in range: $RANGE.$RANGE_START to $RANGE.$RANGE_END for ports $PORT_START to $PORT_END"

TMP_FILE="$(mktemp)"

{
  printf "[\n"
  printf "  {\n"
  printf "    \"targets\": [\n"

  FIRST=1
  i="$RANGE_START"
  while [ "$i" -le "$RANGE_END" ]; do
    IP="$RANGE.$i"
    j="$PORT_START"
    while [ "$j" -le "$PORT_END" ]; do
      PORT="$j"
      if [ "$FIRST" -eq 0 ]; then
        printf ",\n"
      fi
      printf "      \"%s:%s\"" "$IP" "$PORT"
      FIRST=0
      j=$((j + 1))
    done
    i=$((i + 1))
  done

  printf "\n"
  printf "    ],\n"
  printf "    \"labels\": { \"job\": \"known IP range\" }\n"
  printf "  }\n"
  printf "]\n"
} > "$TMP_FILE"

mv "$TMP_FILE" "$OUTFILE"
echo "Wrote targets to $OUTFILE"
