#!/bin/bash
# 위험한 명령어 차단 (PreToolUse hook for Bash)

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

if [ -z "$command" ]; then
  exit 0
fi

# 위험한 명령어 패턴
dangerous_patterns=(
  "rm -rf /"
  "rm -rf ~"
  "rm -rf ."
  "git reset --hard"
  "git clean -fd"
  "DROP TABLE"
  "DROP DATABASE"
  "DELETE FROM"
  "truncate"
)

command_lower=$(echo "$command" | tr '[:upper:]' '[:lower:]')

for pattern in "${dangerous_patterns[@]}"; do
  pattern_lower=$(echo "$pattern" | tr '[:upper:]' '[:lower:]')
  if echo "$command_lower" | grep -q "$pattern_lower"; then
    echo "BLOCKED: Dangerous command detected: $pattern"
    exit 2
  fi
done

exit 0
