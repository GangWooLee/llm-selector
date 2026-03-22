# ApiKeyInput Component Design

> F1. API 키 입력 및 관리 -- 5개 상태, 반응형, 접근성 WCAG AA

---

## 개요

사용자가 OpenRouter API 키를 입력/검증/관리하는 컴포넌트.
상단 고정 바(헤더)에 위치하며, sessionStorage에만 저장한다.

**shadcn/ui 구성**: `Input`, `Button`, `Badge`, `Tooltip`

---

## 상태 다이어그램

```
[empty] --입력+submit--> [validating] --성공--> [valid]
                                      --실패--> [invalid]
[valid] --변경 클릭--> [change] --입력+submit--> [validating]
[invalid] --재입력+submit--> [validating]
[change] --취소--> [valid] (기존 키 복원)
```

---

## 상태별 상세

### 1. Empty (초기 상태)

**시각적 설명**
- 빈 입력 필드 + "분석 시작" 버튼 (비활성)
- 필드 placeholder: "sk-or-... OpenRouter API 키를 입력하세요"
- 입력 필드 좌측에 자물쇠 아이콘 (`LockKeyhole` from lucide-react)

**레이아웃**
```
[LockKeyhole icon] [                Input field                ] [확인 Button]
```

**Tailwind / shadcn**
- Input: `w-full font-mono text-sm placeholder:text-muted-foreground`
- Input type: `password`
- Button: `<Button variant="default" disabled>` (키 없으면 비활성)
- 전체 래퍼: `flex items-center gap-2`

**인터랙션**
- 입력 필드에 포커스하면 `ring-2 ring-ring` 표시
- 텍스트 입력 시 확인 버튼 활성화
- Enter 키 또는 확인 버튼 클릭으로 검증 시작

**전이 조건**
- 키 입력 후 submit -> `validating`

---

### 2. Validating (검증 중)

**시각적 설명**
- 입력 필드 비활성화 (readonly)
- 확인 버튼 -> 스피너로 교체
- 입력 필드 테두리: `border-muted`

**레이아웃**
```
[LockKeyhole icon] [  sk-or-****...****  (readonly)  ] [Spinner]
```

**Tailwind / shadcn**
- Input: `opacity-60 cursor-not-allowed`
- Spinner: `<Loader2 className="animate-spin size-4" />`
- 버튼: `<Button disabled><Loader2 className="animate-spin" /></Button>`

**인터랙션**
- 모든 입력 비활성화
- 타임아웃: 10초 후 자동 실패 처리

**전이 조건**
- 검증 성공 (HTTP 200) -> `valid`
- 검증 실패 (HTTP 401 또는 타임아웃) -> `invalid`

---

### 3. Valid (유효)

**시각적 설명**
- 마스킹된 키 표시: `sk-or-****...****`
- 성공 뱃지: 초록 체크 + "유효" 텍스트
- 잔여 크레딧 표시: `$12.50 남음`
- 변경 버튼

**레이아웃**
```
[Shield-check icon] [sk-or-****...****] [Badge: 유효 | $12.50] [변경 Button]
```

**Tailwind / shadcn**
- 아이콘: `<ShieldCheck className="text-success size-4" />`
- 키 텍스트: `font-mono text-sm text-muted-foreground`
- Badge: `<Badge variant="outline" className="border-success text-success">유효 | $12.50</Badge>`
- 변경 버튼: `<Button variant="ghost" size="sm">변경</Button>`

**인터랙션**
- 변경 버튼 클릭 -> `change` 상태
- 키 텍스트는 읽기 전용 (복사 불가 -- 보안)

**전이 조건**
- 변경 버튼 클릭 -> `change`

---

### 4. Invalid (무효)

**시각적 설명**
- 입력 필드 테두리: 빨간색
- 에러 메시지: 필드 아래에 빨간 텍스트
- 입력 필드에 기존 값 유지 (수정 가능)

**레이아웃**
```
[LockKeyhole icon (red)] [       Input field (red border)       ] [확인 Button]
                          [! 유효하지 않은 API 키입니다. 확인 후 다시 입력하세요.]
```

**Tailwind / shadcn**
- Input: `border-destructive focus-visible:ring-destructive`
- 아이콘: `text-destructive`
- 에러 메시지: `text-xs text-destructive mt-1`
- 진입 시 입력 필드에 `animate-shake` 효과 (1회, 300ms)

**인터랙션**
- 입력 필드에 바로 포커스 (자동)
- 텍스트 수정 시 에러 메시지 유지, submit 시 `validating`으로 전이
- 에러 메시지는 submit 전까지 유지

**전이 조건**
- 키 수정 후 submit -> `validating`

---

### 5. Change (키 변경)

**시각적 설명**
- 기존 키 마스킹 표시 (작게)
- 새 입력 필드 활성화
- 취소 버튼

**레이아웃**
```
[LockKeyhole icon] [        새 키 입력 필드        ] [확인 Button] [취소 Button]
```

**Tailwind / shadcn**
- 새 Input: 기본 스타일 (empty 상태와 동일)
- 확인: `<Button variant="default" size="sm">확인</Button>`
- 취소: `<Button variant="ghost" size="sm">취소</Button>`

**인터랙션**
- 새 키 입력 후 submit -> `validating`
- 취소 클릭 -> `valid` (기존 키 복원)
- Escape 키 -> 취소와 동일

**전이 조건**
- 새 키 submit -> `validating`
- 취소 / Escape -> `valid`

---

## 반응형 설계

### 모바일 (< 768px)
- 전체 너비 (full-width), 헤더 아래 별도 행
- 레이아웃: 수직 스택
```
[ 아이콘 + 입력 필드 (full-width) ]
[ 확인 버튼 (full-width)          ]
[ 에러 메시지 / 상태 뱃지         ]
```
- 입력 필드: `w-full`
- 버튼: `w-full`
- 터치 타겟: 최소 44x44px (`min-h-11`)

### 데스크톱 (>= 768px)
- 헤더 바 우측에 인라인 배치
- 레이아웃: 수평 flex
```
[Logo ... nav]  [아이콘] [Input w-64] [Button] [Badge]
```
- Input: `w-64` (256px)
- 전체: `flex items-center gap-2`

**Tailwind 반응형**
```
래퍼: flex flex-col md:flex-row items-stretch md:items-center gap-2
Input: w-full md:w-64
Button: w-full md:w-auto min-h-11 md:min-h-9
```

---

## 접근성 체크리스트 (WCAG AA)

### 라벨링
- [ ] Input에 `aria-label="OpenRouter API 키"` 설정
- [ ] 에러 상태: `aria-invalid="true"` + `aria-describedby="api-key-error"`
- [ ] 에러 메시지에 `id="api-key-error"` + `role="alert"`
- [ ] 성공 상태: `aria-live="polite"`로 상태 변경 알림

### 포커스 관리
- [ ] 검증 실패 시 입력 필드로 자동 포커스
- [ ] 모든 인터랙티브 요소에 `focus-visible:ring-2 focus-visible:ring-ring` 유지
- [ ] Tab 순서: 입력 필드 -> 확인 버튼 -> 변경/취소 버튼
- [ ] Escape로 change 상태 취소 가능

### 키보드 내비게이션
- [ ] Enter: 검증 submit
- [ ] Escape: change 상태에서 취소
- [ ] Tab / Shift+Tab: 포커스 이동

### 색상 대비
- [ ] 에러 텍스트 (`text-destructive`): 배경 대비 4.5:1 이상
- [ ] 성공 뱃지 텍스트: 배경 대비 4.5:1 이상
- [ ] Placeholder 텍스트: 배경 대비 3:1 이상
- [ ] 색상만으로 상태 전달하지 않음 -- 아이콘 + 텍스트 병행

### 스크린 리더
- [ ] 검증 중: `aria-busy="true"` + "API 키 검증 중" 라이브 리전 알림
- [ ] 검증 성공: "API 키가 유효합니다. 잔여 크레딧 $12.50" 알림
- [ ] 검증 실패: "유효하지 않은 API 키입니다" 알림
- [ ] 마스킹 키: 스크린 리더에 "API 키 설정됨"으로 읽힘 (실제 값 노출 금지)

---

## 에러 상태 상세

| 에러 유형 | 메시지 | 시각적 효과 |
|----------|--------|------------|
| 무효 키 (401) | "유효하지 않은 API 키입니다. 확인 후 다시 입력하세요." | 빨간 테두리 + shake |
| 네트워크 오류 | "연결에 실패했습니다. 잠시 후 다시 시도하세요." | 빨간 테두리 |
| 타임아웃 (10s) | "검증 시간이 초과되었습니다. 다시 시도하세요." | 빨간 테두리 |
| 빈 입력 submit | "API 키를 입력하세요." | 빨간 테두리 + shake |

### Shake 애니메이션
```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-4px); }
  40%, 80% { transform: translateX(4px); }
}
/* Tailwind: animate-shake (커스텀 등록) */
```
