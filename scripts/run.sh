#!/usr/bin/env bash
# Delegate to root run.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
exec bash "$ROOT_DIR/run.sh" "$@"
