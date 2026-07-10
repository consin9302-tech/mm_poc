# 핫딜 수집기 POC (mm_poc)

이 프로젝트는 3대 쇼핑 플랫폼(네이버 쇼핑커넥트, 토스쇼핑 쉐어링크, 쿠팡파트너스)의 핫딜 정보를 자동 수집하고 가격 변동을 비교분석하기 위한 개념 검증(POC) 시스템입니다.

## 🚀 1단계 목표 (쿠팡 파트너스 골드박스 연동)
- 쿠팡 파트너스 골드박스 API를 통해 실시간 특가 상품 목록을 수집합니다.
- 수집된 데이터를 SQLite 로컬 데이터베이스(`hotdeal.db`)에 적재하고, 이전 가격과 현재 가격을 비교합니다.
- 다음 조건 중 하나를 만족하는 상품을 핫딜 후보로 필터링하여 JSON 파일(`hotdeal_poc_output.json`)로 출력합니다:
  - 플랫폼 표시 할인율이 **20% 이상**인 상품
  - 이전 수집 가격 대비 **가격 하락**이 발생한 상품

## 🛠️ 개발 환경 구축
1. **파이썬 환경 구성**: Python 3.12+
2. **패키지 설치**:
   ```bash
   pip install -r requirements.txt
   ```
3. **환경 변수 설정**:
   `hotdeal-collector/.env` 파일을 생성하고 아래 인증 정보를 입력합니다:
   ```env
   COUPANG_ACCESS_KEY=your_access_key
   COUPANG_SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///hotdeal.db
   ```

## 🏃‍♂️ 실행 방법
```bash
cd hotdeal-collector
python main.py
```
