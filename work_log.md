# 작업 히스토리 로그 (Work Log)

이 문서는 핫딜 웹 수집기 프로젝트의 진행 내역과 작업 기록을 관리하는 로그 파일입니다.

---

## 📅 2026-07-10 (금요일) - 직장 PC 개발 환경 구성 및 Git 연동

### 1. 현황 분석 및 계획 수립 [10:35]
- **기존 상태**: 어제 자택에서 작성된 쿠팡 파트너스 API 골드박스 수집 POC 코드(`main.py`, `db.py`, `collector.py`)가 존재함.
- **계획 수립**: 실제 API 연동을 검증하기 위한 상세 계획 수립 및 [implementation_plan.md](file:///C:/Users/DA/.gemini/antigravity-ide/brain/8ecf6735-9ba0-4258-b66e-7243e9e37dae/implementation_plan.md) 승인 완료.

### 2. 로컬 개발 환경 구축 [10:42 ~ 11:05]
- **Python 설치 [10:42]**: 현재 직장 PC에 Python이 설치되어 있지 않음을 식별하고, `winget` 패키지 관리자를 사용하여 **Python 3.12.10**을 사용자 영역에 설치 완료.
- **의존성 패키지 설치 [10:50]**: `pip`를 통해 `requirements.txt`에 명시된 `requests`, `SQLAlchemy`, `python-dotenv` 라이브러리를 정상 설치 완료.
- **환경 변수 구성 [11:54]**: `hotdeal-collector/.env` 파일에 사용자의 실제 쿠팡 API 키(`Access Key`, `Secret Key`) 반영 완료.
- **API 최초 호출 결과 [11:54]**: `python main.py` 실행 결과 쿠팡 API로부터 `401 Unauthorized (Specified key is not registered)` 에러를 수신함. 이는 신규 발급된 쿠팡 API 키가 활성화 및 동기화되기까지 걸리는 대기 시간(최소 1시간 ~ 반나절)에 의한 현상으로 판단되며, 쿠팡 서버 측 동기화 완료 후 재시험 예정.
- **재시도 결과 [11:57]**: 공인 IP(`112.171.68.125`)를 등록 후 재호출하였으나 동일하게 `Specified key is not registered`가 발생했습니다. 쿠팡 파트너스 API 게이트웨이 반영까지 대기 시간이 추가로 필요한 상태입니다.

### 3. Git 및 GitHub 연동 [11:06 ~ 11:13]
- **보안 설정 [11:06]**: `.env` 파일 및 로컬 SQLite DB 파일(`hotdeal.db`)이 퍼블릭 깃허브에 노출되지 않도록 [.gitignore](file:///c:/work/mm/.gitignore) 작성 적용.
- **로컬 저장소 생성 [11:08]**: `git init`을 수행하고 사용자 정보(`CONSIN`, `consin9302@gmail.com`)를 설정한 뒤 최초 커밋 생성.
- **GitHub 원격 저장소 연동 [11:12]**: `https://github.com/consin9302-tech/mm_poc` 레포지토리를 원격(origin)으로 연결하고 최초 푸시(Push) 성공.
- **Git 연동 검증 [11:13]**: `README.md` 작성 및 단위 테스트 코드 추가 후 커밋/푸시를 수행하여, 이후 승인 창이나 로그인 창 없이 원활하게 Git 업로드가 됨을 확인.

### 4. 로직 검증 코드 (Unit Test) 추가 [11:14 ~ 11:15]
- **테스트 시나리오 [11:14]**: DB 저장 및 가격 변동 추적 로직 검증을 위해 [test_db.py](file:///c:/work/mm/hotdeal-collector/test_db.py) 작성.
  - 신규 상품 최초 DB 적재 테스트
  - 동일 가격 재수집 시 변동 없음 처리 테스트
  - 가격 하락 시 이전 가격 기록 및 변동 알림(is_changed) 감지 테스트
- **테스트 결과 [11:15]**: 3개 테스트 케이스 모두 통과(OK).

### 5. 수집기 구조 개편 및 플랫폼 확장 준비 (네이버, 토스) [11:29 ~ 11:31]
- **추상화 패키지 구성 [11:29]**: `hotdeal-collector/collectors/` 디렉토리를 신설하고 공통 인터페이스 `BaseCollector`([base.py](file:///c:/work/mm/hotdeal-collector/collectors/base.py))를 정의함.
- **수집기 모듈 분리 [11:30]**:
  - [coupang.py](file:///c:/work/mm/hotdeal-collector/collectors/coupang.py): 기존 쿠팡 골드박스 수집 로직 이관 및 인터페이스 맞춤 구현.
  - [naver.py](file:///c:/work/mm/hotdeal-collector/collectors/naver.py): 네이버 쇼핑커넥트 연동 대비용 스켈레톤(Stub 데이터) 모듈 작성.
  - [toss.py](file:///c:/work/mm/hotdeal-collector/collectors/toss.py): 토스쇼핑 쉐어링크 연동 대비용 스켈레톤(Stub 데이터) 모듈 작성.
- **호환성 및 리팩토링 [11:30]**: `collector.py`는 하위 호환용 래퍼로 수정하고, `main.py` 수집기 진입점을 `collectors` 패키지로 전환 완료.
- **확장성 테스트 추가 [11:31]**: 신규 설계 구조와 네이버/토스 스텁 작동 확인을 위해 [test_collectors.py](file:///c:/work/mm/hotdeal-collector/test_collectors.py) 테스트 코드를 작성하고 전체 테스트(`discover` 명령어로 총 6개 테스트 통과) 성공 검증 및 Git 푸시 완료.

---

## 📋 향후 작업 예정 사항 (To-Do)
- [ ] **쿠팡 Partners API 키 입력**: 발급 완료 후 `.env` 파일에 `COUPANG_ACCESS_KEY` 및 `COUPANG_SECRET_KEY` 반영.
- [ ] **POC 1차 수집 실행**: `python main.py` 실행하여 실제 API 응답 데이터가 DB에 정상 적재되는지 및 `hotdeal_poc_output.json` 결과물이 올바르게 생성되는지 확인.
- [ ] **가격 하락 필터링 검증**: DB 수동 가격 조작 후 재수집하여 가격 하락 할인율 계산이 성공 기준에 부합하는지 최종 확인.
- [ ] **본 개발 단계 이행**: POC 검증 통과 후 `hotdeal-web-collector-plan-v0.1.md`에 근거한 웹 대시보드(FastAPI + React) 아키텍처 설계 및 본 개발 착수.

