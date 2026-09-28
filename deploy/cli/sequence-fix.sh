#!/usr/bin/env bash

movo_fix_recover_on_exit() {
  local original_status=$?
  trap - EXIT INT TERM
  if [[ "${MOVO_FIX_RESTORE_PENDING:-false}" != "true" ]]; then
    return "${original_status}"
  fi
  MOVO_FIX_RESTORE_PENDING=false
  if [[ "${MOVO_FIX_BACKUP_VALID:-false}" == "true" ]]; then
    movo_msg fix_restoring >&2
    if ! movo_compose exec -T mongo mongorestore --drop --archive --gzip \
        --nsInclude='gragentic.chat_messages' \
        --nsInclude='gragentic.chat_sessions' \
        --nsInclude='gragentic.session_participants' < "${MOVO_FIX_BACKUP_FILE}"; then
      movo_msg fix_restore_failed "${MOVO_FIX_BACKUP_DIR}" >&2
      exit 1
    fi
  fi
  if ! movo_compose start chat-api; then
    movo_msg fix_restore_failed "${MOVO_FIX_BACKUP_DIR}" >&2
    exit 1
  fi
  if [[ -n "${MOVO_FIX_MARKER:-}" ]]; then
    rm -f "${MOVO_FIX_MARKER}"
  fi
  if [[ "${MOVO_FIX_BACKUP_VALID:-false}" == "true" ]]; then
    movo_msg fix_rolled_back "${MOVO_FIX_BACKUP_DIR}" >&2
  fi
  return "${original_status}"
}

movo_fix_sequences() {
  local confirmed="false" use_build="false" argument backup_dir backup_file backup_base marker
  for argument in "$@"; do
    case "${argument}" in
      --yes) confirmed="true" ;;
      --build) use_build="true" ;;
      *) printf 'Unknown fix option: %s\n' "${argument}" >&2; return 2 ;;
    esac
  done
  if [[ "${confirmed}" != "true" ]]; then
    if [[ ! -t 0 ]]; then
      movo_msg fix_confirm >&2
      return 2
    fi
    local answer=""
    movo_msg fix_confirm
    read -r answer
    [[ "${answer}" == "FIX" ]] || return 2
  fi

  if [[ "${use_build}" == "true" ]]; then
    movo_configure_images true
    movo_compose build chat-api || return 1
  else
    movo_configure_images false
    MOVO_PULL_POLICY=always
    export MOVO_PULL_POLICY
    movo_pull_images_serially always || return 1
  fi
  # Check prerequisites before taking the writer offline. The official Mongo
  # image ships both tools; a custom image must supply them too.
  if ! movo_compose exec -T mongo sh -c \
      'command -v mongodump && command -v mongorestore && mongorestore --help | grep -q -- --dryRun' >/dev/null; then
    movo_msg fix_tools_missing >&2
    return 1
  fi
  backup_base="${MOVO_FIX_BACKUP_BASE_DIR:-${ROOT_DIR}/backups}"
  mkdir -p "${backup_base}"
  for marker in "${backup_base}"/session-seq-fix.*/IN_PROGRESS; do
    if [[ -f "${marker}" ]]; then
      movo_msg fix_incomplete "${marker%/IN_PROGRESS}" >&2
      return 1
    fi
  done
  if [[ -z "$(movo_compose ps -q chat-api 2>/dev/null || true)" ]]; then
    movo_msg fix_requires_running_chat >&2
    return 1
  fi
  backup_dir="$(umask 077; mktemp -d "${backup_base}/session-seq-fix.XXXXXXXX")"
  backup_file="${backup_dir}/mongo.archive.gz"

  movo_msg fix_stopping
  if ! movo_compose stop -t 600 chat-api; then
    movo_compose start chat-api || true
    return 1
  fi
  if [[ -n "$(movo_compose ps -q chat-api 2>/dev/null || true)" ]]; then
    movo_msg fix_writer_still_running >&2
    movo_compose start chat-api || true
    return 1
  fi
  MOVO_FIX_BACKUP_DIR="${backup_dir}"
  MOVO_FIX_BACKUP_FILE="${backup_file}"
  MOVO_FIX_BACKUP_VALID=false
  MOVO_FIX_RESTORE_PENDING=true
  trap 'movo_fix_recover_on_exit' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  if ! movo_compose exec -T mongo mongodump --db gragentic --archive --gzip > "${backup_file}"; then
    movo_msg fix_backup_failed >&2
    return 1
  fi
  if [[ ! -s "${backup_file}" ]]; then
    movo_msg fix_backup_failed >&2
    return 1
  fi
  if ! movo_compose exec -T mongo mongorestore --dryRun --archive --gzip \
      --nsInclude='gragentic.chat_messages' \
      --nsInclude='gragentic.chat_sessions' \
      --nsInclude='gragentic.session_participants' < "${backup_file}"; then
    movo_msg fix_backup_failed >&2
    return 1
  fi
  MOVO_FIX_BACKUP_VALID=true
  MOVO_FIX_MARKER="${backup_dir}/IN_PROGRESS"
  printf '%s\n' "${MOVO_VERSION}" > "${MOVO_FIX_MARKER}"
  movo_msg fix_backup_complete "${backup_dir}"

  if movo_compose run --rm --no-deps --pull never \
      -e MOVO_SESSION_FIX_WRITES_STOPPED=1 chat-api \
      python -m app.migrations.sequence_repair \
    && movo_run_database_upgrade fix; then
    rm -f "${MOVO_FIX_MARKER}"
    MOVO_FIX_RESTORE_PENDING=false
    trap - EXIT INT TERM
    if [[ "${use_build}" == "true" ]]; then
      movo_msg fix_complete_build
    else
      movo_msg fix_complete
    fi
    return 0
  fi
  return 1
}
