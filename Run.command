#!/bin/zsh
set -eu
HERE="${0:A:h}"
UV="$(command -v uv || true)"
if [[ -z "$UV" ]]; then
  for candidate in "$HOME/.local/bin/uv" /opt/homebrew/bin/uv /usr/local/bin/uv "$HOME/.cargo/bin/uv"; do
    if [[ -x "$candidate" ]]; then UV="$candidate"; break; fi
  done
fi
if [[ -z "$UV" ]]; then
  print "uv was not found. Install uv from https://docs.astral.sh/uv/ then run again."
  read "?Press Enter to close."
  exit 1
fi
if ! "$UV" run "$HERE/start.py" "$@"; then
  print "Launcher failed. Read the message above (the port may already be in use)."
  read "?Press Enter to close."
  exit 1
fi
