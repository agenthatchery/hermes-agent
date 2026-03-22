#!/usr/bin/env bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-/home/hermes/.hermes}"
HERMES_ENV_SECRET="${HERMES_ENV_SECRET:-/run/secrets/hermes_env}"
HERMES_CONFIG_SECRET="${HERMES_CONFIG_SECRET:-/run/secrets/hermes_config}"

mkdir -p "${HERMES_HOME}"

copy_if_missing() {
  local src="$1"
  local dst="$2"

  if [[ -f "${src}" && ! -f "${dst}" ]]; then
    cp "${src}" "${dst}"
    chmod 600 "${dst}"
  fi
}

copy_if_missing "${HERMES_ENV_SECRET}" "${HERMES_HOME}/.env"
copy_if_missing "${HERMES_CONFIG_SECRET}" "${HERMES_HOME}/config.yaml"

mkdir -p \
  "${HERMES_HOME}/cron" \
  "${HERMES_HOME}/sessions" \
  "${HERMES_HOME}/logs" \
  "${HERMES_HOME}/skills" \
  "${HERMES_HOME}/memories" \
  "${HERMES_HOME}/image_cache" \
  "${HERMES_HOME}/audio_cache" \
  "${HERMES_HOME}/pairing" \
  "${HERMES_HOME}/whatsapp/session" \
  "${HERMES_HOME}/output"

# Keep a bootstrap copy when launching first time from persistent volume.
if [[ -f /opt/hermes-templates/.env.example && ! -f "${HERMES_HOME}/.env.example" ]]; then
  cp /opt/hermes-templates/.env.example "${HERMES_HOME}/.env.example"
fi

if [[ -f /opt/hermes-templates/cli-config.yaml.example && ! -f "${HERMES_HOME}/config.yaml" ]]; then
  cp /opt/hermes-templates/cli-config.yaml.example "${HERMES_HOME}/config.yaml"
fi

exec "$@"
