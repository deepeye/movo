#!/usr/bin/env bash

# Run the new image's additive migrations before replacing a running chat-api.
# The container joins the existing Compose network but does not start any deps.
movo_run_database_upgrade() {
  local context="${1:-upgrade}"
  movo_msg upgrading_database
  if ! movo_compose run --rm --no-deps --pull never chat-api \
    python -m app.migrations; then
    if [[ "${context}" != "fix" ]]; then
      movo_msg upgrade_database_failed >&2
    fi
    return 1
  fi
}

movo_upgrade_database_if_running() {
  local running_chat_api
  running_chat_api="$(movo_compose ps -q chat-api 2>/dev/null || true)"
  if [[ -n "${running_chat_api}" ]]; then
    movo_run_database_upgrade
  fi
}
