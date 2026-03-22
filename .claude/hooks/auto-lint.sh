#!/bin/bash
# 파일 수정 후 자동 린트 (PostToolUse hook for Write|Edit)

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

if [ -z "$file_path" ]; then
  exit 0
fi

# Python 파일 → ruff format
if echo "$file_path" | grep -qE '\.py$'; then
  if command -v ruff &>/dev/null; then
    ruff format "$file_path" 2>/dev/null || true
  fi
fi

# TypeScript/TSX 파일은 자동 수정하지 않음 (빌드 시 lint로 검증)

exit 0
