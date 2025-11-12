#!/usr/bin/env bash
set -euo pipefail
docker compose --profile build run --rm scala-builder
