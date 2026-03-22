#!/bin/bash
# 보호 파일 쓰기 차단 (PreToolUse hook for Write|Edit)

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

if [ -z "$file_path" ]; then
  exit 0
fi

# 보호 대상 패턴
protected_patterns=(
  ".env"
  ".env.local"
  ".env.production"
  "package-lock.json"
  "pnpm-lock.yaml"
  "bun.lock"
  ".git/"
)

for pattern in "${protected_patterns[@]}"; do
  if echo "$file_path" | grep -q "$pattern"; then
    echo "BLOCKED: Protected file cannot be modified: $file_path"
    exit 2
  fi
done

exit 0
