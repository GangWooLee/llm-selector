#!/bin/bash
# 컨텍스트 압축 전 현재 상태 저장

echo "[Pre-Compact] Saving context state..."
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
echo "Modified files: $(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')"
echo "Staged files: $(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')"
echo "Last commit: $(git log --oneline -1 2>/dev/null || echo 'N/A')"

exit 0
