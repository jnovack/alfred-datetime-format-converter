#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOW_DIR="${ROOT_DIR}/workflow"
DIST_DIR="${ROOT_DIR}/dist"
OUTPUT_FILE="${DIST_DIR}/DatetimeFormatConverter.alfredworkflow"

mkdir -p "${DIST_DIR}"
rm -f "${OUTPUT_FILE}"

(
  cd "${WORKFLOW_DIR}"
  zip -r "${OUTPUT_FILE}" . -x "*.DS_Store"
)

echo "Built ${OUTPUT_FILE}"
