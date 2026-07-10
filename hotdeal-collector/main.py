import os
import json
from dotenv import load_dotenv
from db import init_db, SessionLocal, save_or_update_product
from collector import CoupangPartnersClient

# .env 파일 로드 (만약 존재할 경우)
load_dotenv()

def run_poc():
    print("=========================================")
    print(" 핫딜 수집기 POC (쿠팡 골드박스) 실행 시작")
    print("=========================================")

    # 1. DB 초기화
    init_db()
    session = SessionLocal()

    # 2. 쿠팡 파트너스 API 클라이언트 선언
    # 환경변수에서 COUPANG_ACCESS_KEY 및 COUPANG_SECRET_KEY 로드
    access_key = os.getenv("COUPANG_ACCESS_KEY")
    secret_key = os.getenv("COUPANG_SECRET_KEY")
    
    if not access_key or not secret_key:
        print("[오류] .env 파일 또는 환경 변수에 COUPANG_ACCESS_KEY와 COUPANG_SECRET_KEY가 설정되어 있지 않습니다.")
        print("프로젝트 내에 .env 파일을 생성하고 아래 형식을 기입해 주세요:")
        print("COUPANG_ACCESS_KEY=your_key")
        print("COUPANG_SECRET_KEY=your_key")
        return

    client = CoupangPartnersClient(access_key=access_key, secret_key=secret_key)

    # 3. 골드박스 상품 목록 수집
    print("-> 쿠팡 골드박스 API 호출 중...")
    collected_products = client.get_goldbox_products()
    
    if not collected_products:
        print("[경고] 수집된 상품이 없거나 API 호출에 실패했습니다. 키 정보 또는 네트워크를 확인하세요.")
        return

    print(f"-> 총 {len(collected_products)}개의 상품 수집 완료. DB 비교 및 적재 시작...")

    # 4. DB 적재 및 비교 진행
    poc_results = []
    
    for item in collected_products:
        # DB 저장 및 비교 헬퍼 호출
        product_obj, is_changed, prev_price, curr_price = save_or_update_product(
            session=session,
            platform="coupang",
            product_id=item["product_id"],
            title=item["title"],
            image_url=item["image_url"],
            original_url=item["original_url"],
            price=item["price"],
            discount_rate=item["discount_rate"]
        )
        
        # 분석 항목 저장
        poc_results.append({
            "product_id": item["product_id"],
            "title": item["title"],
            "price": curr_price,
            "prev_price": prev_price,
            "discount_rate": item["discount_rate"],
            "is_changed": is_changed,
            "original_url": item["original_url"]
        })

    # 세션 커밋 (영구 보존)
    session.commit()
    session.close()
    print("-> DB 적재 완료.")

    # 5. 조건 필터링 및 리스트 아웃풋 (Output)
    # POC 조건: 할인율이 20% 이상이거나, 기존 대비 가격 변동(하락)이 있는 상품 선별
    print("\n=========================================")
    print("       ★ 조건에 맞는 핫딜 리스트 ★")
    print("=========================================")
    
    hotdeals = []
    for item in poc_results:
        # 조건 A: 할인율 20% 이상
        # 조건 B: 가격 하락 변동 발생 (이전 가격이 있고, 현재 가격이 더 낮음)
        is_hotdeal = False
        reason = []
        
        if item["discount_rate"] >= 20:
            is_hotdeal = True
            reason.append(f"할인율 {item['discount_rate']}%")
            
        if item["prev_price"] is not None and item["price"] < item["prev_price"]:
            is_hotdeal = True
            saving = item["prev_price"] - item["price"]
            reason.append(f"이전 대비 {saving:,}원 가격 하락")
            
        if is_hotdeal:
            hotdeals.append(item)
            print(f"- [추천] {item['title'][:40]}...")
            print(f"  가격: {item['price']:,}원 | 조건: {', '.join(reason)}")
            print(f"  링크: {item['original_url']}")
            print("-" * 40)

    print(f"총 {len(hotdeals)}개의 핫딜을 분류해 냈습니다.")

    # 6. JSON 파일로 아웃풋 저장
    output_filename = "hotdeal_poc_output.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(hotdeals, f, ensure_ascii=False, indent=4)
        
    print(f"\n-> 결과가 '{output_filename}' 파일로 저장되었습니다.")
    print("=========================================")

if __name__ == "__main__":
    run_poc()
