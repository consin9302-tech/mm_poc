# 핫딜 웹 수집기 v0.1 기획

작성: 2026-07-09 KST

## 한 줄 목표

관리자가 웹페이지에서 자동 수집된 핫딜 후보를 보고, 가격 판정 상태와 게시글 초안을 확인·승인·보류·폐기할 수 있게 만든다.

## 핵심 원칙

- 수동 상품 링크 입력은 기본 흐름에서 제외한다.
- 웹페이지는 "운영 대시보드" 역할을 한다.
- v0.1은 자동 발송하지 않는다.
- 수집된 링크와 상품은 전부 이력으로 남긴다.
- 상태값을 명확히 둬서 사람이 어디까지 검토됐는지 바로 알 수 있게 한다.

## 사용자 흐름

```text
1. 시스템이 주기적으로 상품 후보 자동 수집
2. 웹페이지 > 수집 내역에서 후보 목록 확인
3. 각 후보의 가격/단위가/점수/근거 확인
4. 상태 변경: 신규 → 검토중 → 승인후보/보류/폐기/만료
5. 승인후보는 게시글 초안 확인
6. 발송 기능은 v0.2 이후 별도 결정
```

## 화면 구성

### 1. 대시보드 Home

목적: 오늘 상태를 한눈에 본다.

표시 항목:

- 오늘 수집된 후보 수
- 신규 후보 수
- 승인후보 수
- 보류 수
- 폐기 수
- 만료/품절 수
- 평균 점수
- 상위 후보 TOP 5
- 수집 실패/오류 로그 요약

예시 카드:

```text
오늘 수집 124개
신규 38개
승인후보 7개
보류 12개
폐기 61개
만료 6개
```

### 2. 수집 내역 List

목적: 자동 수집된 링크/상품을 테이블로 본다.

필터:

- 상태
- 등급
- 카테고리
- 수집 출처
- 점수 범위
- 가격대
- 품절 여부
- 키워드
- 수집 날짜

테이블 컬럼:

- 체크박스
- 상태
- 등급
- 점수
- 상품명
- 현재가
- 단위가
- 배송비
- 수집 출처
- 수집 키워드
- 수집 시각
- 마지막 가격 확인 시각
- 링크
- 액션

상태 뱃지 예시:

- 신규
- 분석중
- 승인후보
- 보류
- 폐기
- 만료
- 품절
- 가격변동
- 오류

액션:

- 상세 보기
- 원본 링크 열기
- 가격 재확인
- 승인후보로 변경
- 보류
- 폐기

### 3. 후보 상세 Detail

목적: 이 상품이 왜 좋은지/아닌지 판단한다.

섹션:

1. 기본 정보
   - 상품명
   - 이미지
   - 브랜드
   - 카테고리
   - 옵션/수량
   - 현재가
   - 배송비
   - 최종가
   - 원본 링크
   - 제휴 링크, 있으면

2. 가격 분석
   - 단위가
   - 최근 7일 평균가
   - 최근 30일 평균가
   - 최근 90일 평균가
   - 최근 90일 최저가
   - 평균 대비 할인율
   - 최저가 대비 차이

3. 점수 근거
   - 가격 매력도
   - 단위가 경쟁력
   - 후기/평점
   - 재구매성
   - 재현성
   - 리스크 감점

4. 상태 이력
   - 언제 수집됨
   - 언제 분석됨
   - 가격 변동 여부
   - 사람이 변경한 상태 로그

5. 게시글 초안
   - 자동 생성 문구
   - 복사 버튼
   - 수정 가능 textarea
   - 제휴 고지 자동 포함

### 4. 수집 설정 Sources

목적: 어디서 무엇을 수집할지 관리한다.

설정 항목:

- 수집 소스
  - 네이버쇼핑
  - 쿠팡 파트너스 API
  - 알리/11번가 등 추후 추가
- 키워드 그룹
  - 생필품
  - 식품
  - 가전
  - 육아
  - 반려동물
- 키워드별 주기
- 키워드별 최대 후보 수
- 최소 점수 기준
- 제외어
- 포함어
- 가격대 제한

키워드 예시:

```text
물티슈 100매 20팩
안성탕면 15개
액체세제 2.5L
쌀 10kg
제습기 13L
```

### 5. 실행 로그 Logs

목적: 수집기가 왜 실패했는지 확인한다.

표시 항목:

- 실행 시각
- 수집 소스
- 키워드
- 요청 수
- 성공 수
- 실패 수
- 오류 메시지
- 소요 시간

## 상태 모델

### Deal Status

```text
NEW          신규 수집됨
ANALYZING    가격/단위가/시장가 분석 중
CANDIDATE    점수 기준 통과, 승인후보
REVIEWING    사람이 검토 중
HOLD         보류
APPROVED     승인됨, v0.1에서는 발송 안 함
REJECTED     폐기
EXPIRED      가격 만료 또는 링크 만료
SOLD_OUT     품절
PRICE_CHANGED 가격 변동으로 재검토 필요
ERROR        분석 실패
```

### 상태 전이

```text
NEW → ANALYZING → CANDIDATE
NEW → ANALYZING → REJECTED
CANDIDATE → REVIEWING → APPROVED
CANDIDATE → REVIEWING → HOLD
CANDIDATE → REVIEWING → REJECTED
APPROVED → PRICE_CHANGED
APPROVED → EXPIRED
any → ERROR
any → SOLD_OUT
```

## 데이터 모델 초안

### collected_links

- id
- source
- source_keyword
- original_url
- normalized_url
- affiliate_url
- first_seen_at
- last_seen_at
- status
- error_message

### products

- id
- product_key
- title_raw
- title_normalized
- brand
- category
- image_url
- package_signature
- created_at

### price_observations

- id
- product_id
- source
- collected_link_id
- observed_at
- current_price
- shipping_fee
- final_price
- unit_price
- unit_label
- availability
- review_count
- rating

### deal_candidates

- id
- product_id
- collected_link_id
- status
- grade
- score
- evidence_json
- generated_post
- human_note
- created_at
- updated_at
- expires_at

### status_events

- id
- candidate_id
- from_status
- to_status
- reason
- actor
- created_at

## API 초안

```text
GET    /api/dashboard
GET    /api/candidates
GET    /api/candidates/:id
POST   /api/candidates/:id/recheck-price
PATCH  /api/candidates/:id/status
PATCH  /api/candidates/:id/post
GET    /api/sources
PATCH  /api/sources/:id
POST   /api/collector/run
GET    /api/logs
```

## 기술 스택 제안

작게 시작하는 기준:

- Frontend: React + Vite
- Backend: FastAPI 또는 Node/Express
- DB: SQLite
- Scheduler: APScheduler 또는 cron
- Collector: Python 어댑터 구조

내 추천:

```text
Python FastAPI + SQLite + React/Vite
```

이유:

- 가격 파싱/수집/점수화 로직은 Python이 편함
- 초기 배포가 단순함
- 나중에 Playwright 브라우저 자동화 붙이기 쉬움
- SQLite로 시작해도 충분함

## v0.1 구현 범위

### 포함

- 웹 대시보드
- 수집 내역 테이블
- 후보 상세 화면
- 상태 변경
- 게시글 초안 보기/수정
- SQLite 저장
- 수집 설정 화면의 최소 버전
- 수동 실행 버튼: "지금 수집"
- 자동 발송 없음

### 제외

- 카카오톡/텔레그램/디스코드 자동 발송
- 결제/회원 기능
- 다중 운영자 권한
- 완전한 쿠팡 카드할인 재현
- 고도화된 상품 매칭 AI

## Builder 작업 카드 v0.1

### Goal

핫딜 자동 수집 웹 대시보드의 프로토타입을 만든다.

### Scope

- 새 프로젝트: `hotdeal-collector/`
- Backend API
- SQLite schema
- Frontend pages
  - Dashboard
  - Candidate List
  - Candidate Detail
  - Sources/Settings 최소 화면
- 샘플 수집 어댑터
  - 실제 API 키가 없으면 fixture 기반 + collector interface 구현

### Forbidden

- 자동 발송 구현 금지
- 제휴 링크를 실제로 외부 발송 금지
- 크롤링 약관 우회 코드 금지
- 사용자의 개인 토큰/쿠키 하드코딩 금지

### Verification

- backend test 통과
- frontend build 통과
- seed 데이터로 후보 목록 표시
- 상태 변경 API 동작
- 게시글 초안 수정 저장 동작

### PASS 기준

- 브라우저에서 수집 내역 목록이 보임
- 후보 상세에서 가격 근거/상태/초안 확인 가능
- 상태 변경 후 이력이 남음
- 자동 발송 기능이 없음

## 다음 결정 필요 사항

1. 프로젝트 위치
   - 기본 제안: `/Users/wo_ong/.openclaw/workspace/hotdeal-collector`
2. 첫 수집 소스
   - 네이버쇼핑 검색 API 우선 추천
3. UI 톤
   - 운영툴형, 단순하고 빠르게
4. 인증 필요 여부
   - 로컬 전용이면 v0.1 인증 생략 가능
   - 외부 공개면 로그인 필수
