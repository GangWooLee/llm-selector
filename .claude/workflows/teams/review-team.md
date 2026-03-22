# Review Team — Pre-PR 전문 리뷰 팀

## 사용 시점
PR 전, Phase 경계, 에이전트/SSE/DB 수정 후

## 구성 (5명 + lead, 모두 plan 읽기전용)

| 역할 | 모델 | 모드 | 전담 리뷰 영역 |
|------|------|------|--------------|
| lead | opus | default | 조율, 리뷰 통합, 머지 결정 |
| **security-reviewer** | opus | plan | API 키 보안, CORS, 인젝션, XSS, 입력 검증 |
| **performance-reviewer** | opus | plan | N+1 쿼리, SSE 효율, 번들 사이즈, async 정확성 |
| **sse-reviewer** | opus | plan | SSE 이벤트 흐름, 에이전트→스트림 브릿지, 에러 전파, 버퍼링 |
| **agent-reviewer** | opus | plan | 에이전트 프롬프트 품질, 도구 docstring, 출력 스키마 정합성 |
| **design-reviewer** | opus | plan | UI 접근성, 반응형, shadcn/ui 활용, 사용성 |

## 실행 흐름

1. lead: `git diff main...HEAD` → 변경 범위 파악 + 5개 태스크 생성
2. 5명 병렬 리뷰 (모두 plan 모드, 코드 수정 불가)
3. 각 리뷰어 → lead에 SendMessage로 결과 보고
4. lead: Critical / Warning / Info 분류 → 최종 요약

## 리뷰어별 체크리스트

### security-reviewer
- [ ] API 키가 서버에 저장/로그되지 않음
- [ ] 프론트엔드: sessionStorage만 사용
- [ ] raw SQL 없음 (ORM만)
- [ ] CORS 명시적 도메인만 허용
- [ ] Pydantic 모델에 길이 제한
- [ ] `dangerouslySetInnerHTML` 없음

### performance-reviewer
- [ ] `selectinload`/`joinedload` 사용 (N+1 방지)
- [ ] 필터 컬럼에 인덱스 존재
- [ ] 불필요한 `"use client"` 없음
- [ ] SSE cleanup (AbortController)
- [ ] 에이전트 타임아웃 120초

### sse-reviewer
- [ ] 6개 이벤트 타입 프로토콜 준수
- [ ] `format_sse` 포맷 정확 (`event: ...\ndata: ...\n\n`)
- [ ] 프론트엔드 파서 버퍼 경계 처리
- [ ] 에러 전파 체인 완전
- [ ] 헤더: `Cache-Control: no-cache`, `X-Accel-Buffering: no`

### agent-reviewer
- [ ] 시스템 프롬프트에 "자체 지식 금지" 명시
- [ ] 모든 도구에 타입 힌트 + docstring
- [ ] 출력 스키마(ComparisonReport)와 프론트 타입 일치
- [ ] 도구가 queries.py만 사용 (DB 직접 접근 금지)
- [ ] 에이전트 실행 타임아웃 설정

### design-reviewer
- [ ] 터치 타겟 44x44px, 본문 16px
- [ ] 색상 대비 4.5:1 (WCAG AA)
- [ ] `aria-label`, `htmlFor` 필수 항목
- [ ] 모바일/태블릿/데스크톱 반응형
- [ ] shadcn/ui 컴포넌트 우선 활용
