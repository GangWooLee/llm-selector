#!/bin/bash
# macOS 데스크톱 알림

input=$(cat)
title=$(echo "$input" | jq -r '.title // "Claude Code"')
message=$(echo "$input" | jq -r '.message // "작업 완료"')

osascript -e "display notification \"$message\" with title \"$title\"" 2>/dev/null || true

exit 0
