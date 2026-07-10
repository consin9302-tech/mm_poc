import os
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn

from db import init_db, SessionLocal, Product, PriceHistory, save_or_update_product
from collectors import (
    CoupangPartnersClient,
    NaverShoppingConnectClient,
    TossShoppingShareLinkClient
)

app = FastAPI(title="핫딜 웹 수집기 대시보드")

# DB 초기화 및 웹용 시드 데이터 적재
init_db()

def seed_initial_data_if_empty():
    session = SessionLocal()
    try:
        if session.query(Product).count() == 0:
            print("-> 데이터베이스가 비어 있습니다. 초기 데모 데이터를 적재합니다...")
            # 1. 쿠팡 파트너스 데모 데이터 (API 키 만료 시를 대비한 오프라인 시드)
            coupang_seeds = [
                {
                    "product_id": "cp_1001",
                    "title": "[골드박스] 크리넥스 데코앤소프트 3겹 화장지 30m x 30롤",
                    "image_url": "https://thumbnail.coupangcdn.com/thumbnails/remote/490x490ex/image/retail/images/2020/06/17/14/0/55a15321-4ea6-4277-9df0-06f1eb8ba040.jpg",
                    "original_url": "https://link.coupang.com/a/demo1",
                    "price": 22900,
                    "discount_rate": 28.0
                },
                {
                    "product_id": "cp_1002",
                    "title": "[골드박스] 햇반 발아현미밥 210g x 36개입",
                    "image_url": "https://thumbnail.coupangcdn.com/thumbnails/remote/490x490ex/image/retail/images/2021/08/10/11/4/2103f622-c3df-498c-8c01-6c2e39d37532.jpg",
                    "original_url": "https://link.coupang.com/a/demo2",
                    "price": 31900,
                    "discount_rate": 18.0
                }
            ]
            for item in coupang_seeds:
                save_or_update_product(
                    session, "coupang", item["product_id"], item["title"],
                    item["image_url"], item["original_url"], item["price"], item["discount_rate"]
                )
            
            # 2. 네이버 & 토스 스텁 데이터 호출하여 적재
            naver_client = NaverShoppingConnectClient()
            toss_client = TossShoppingShareLinkClient()
            
            for item in naver_client.collect():
                save_or_update_product(
                    session, "naver", item["product_id"], item["title"],
                    item["image_url"], item["original_url"], item["price"], item["discount_rate"]
                )
            for item in toss_client.collect():
                save_or_update_product(
                    session, "toss", item["product_id"], item["title"],
                    item["image_url"], item["original_url"], item["price"], item["discount_rate"]
                )
            
            session.commit()
            print("-> 초기 데모 데이터 적재가 완료되었습니다.")
    except Exception as e:
        print(f"[오류] 데모 데이터 적재 실패: {e}")
    finally:
        session.close()

seed_initial_data_if_empty()


# static 디렉토리 생성 확인 후 마운트
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/deals")
def get_deals(
    platform: str = Query(None, description="수집 플랫폼 필터 (coupang, naver, toss)"),
    search: str = Query(None, description="상품명 검색어"),
    sort_by: str = Query("discount", description="정렬 기준 (discount, price_asc, price_desc, title)")
):
    session = SessionLocal()
    try:
        # 각 상품별 최신 가격 이력 정보를 함께 가져오기
        # SQLAlchemy Query 조인 구성
        query = session.query(Product)
        
        if platform:
            query = query.filter(Product.platform == platform)
            
        if search:
            query = query.filter(Product.title.contains(search))
            
        products = query.all()
        deal_list = []
        
        for p in products:
            # 최신 가격 데이터 획득
            latest_history = session.query(PriceHistory).filter(
                PriceHistory.product_id == p.id
            ).order_by(PriceHistory.observed_at.desc()).first()
            
            if not latest_history:
                continue
                
            # 가격 변경 이력 개수 카운트
            history_count = session.query(PriceHistory).filter(PriceHistory.product_id == p.id).count()
            
            # 이전 가격 찾기 (최신 이력 바로 직전 이력)
            prev_price = None
            if history_count > 1:
                prev_history = session.query(PriceHistory).filter(
                    PriceHistory.product_id == p.id
                ).order_by(PriceHistory.observed_at.desc()).offset(1).first()
                if prev_history:
                    prev_price = prev_history.price
            
            deal_list.append({
                "id": p.id,
                "platform": p.platform,
                "product_id": p.product_id,
                "title": p.title,
                "image_url": p.image_url,
                "original_url": p.original_url,
                "price": latest_history.price,
                "prev_price": prev_price,
                "discount_rate": latest_history.discount_rate,
                "observed_at": latest_history.observed_at.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        # 정렬 처리
        if sort_by == "discount":
            deal_list.sort(key=lambda x: x["discount_rate"] or 0, reverse=True)
        elif sort_by == "price_asc":
            deal_list.sort(key=lambda x: x["price"])
        elif sort_by == "price_desc":
            deal_list.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "title":
            deal_list.sort(key=lambda x: x["title"])
            
        return deal_list
    finally:
        session.close()

@app.get("/api/collect")
def run_collection():
    session = SessionLocal()
    collected_count = 0
    errors = []
    
    # 각 플랫폼별 클라이언트 초기화
    clients = {
        "coupang": CoupangPartnersClient(),
        "naver": NaverShoppingConnectClient(),
        "toss": TossShoppingShareLinkClient()
    }
    
    try:
        for platform, client in clients.items():
            print(f"-> {platform} 데이터 수집 중...")
            try:
                products = client.collect()
                for item in products:
                    save_or_update_product(
                        session=session,
                        platform=platform,
                        product_id=item["product_id"],
                        title=item["title"],
                        image_url=item["image_url"],
                        original_url=item["original_url"],
                        price=item["price"],
                        discount_rate=item["discount_rate"]
                    )
                    collected_count += 1
            except Exception as pe:
                err_msg = f"{platform} 수집 실패: {str(pe)}"
                print(f"[경고] {err_msg}")
                errors.append(err_msg)
                
        session.commit()
        return {
            "status": "success" if not errors else "partial_success",
            "collected_count": collected_count,
            "errors": errors,
            "message": f"총 {collected_count}개의 상품 정보 업데이트 완료."
        }
    except Exception as e:
        session.rollback()
        return {"status": "error", "message": f"수집기 구동 실패: {str(e)}"}
    finally:
        session.close()

if __name__ == "__main__":
    print("=========================================")
    print(" 핫딜 대시보드 웹 서버 구동 (http://localhost:8000)")
    print("=========================================")
    uvicorn.run("main_web:app", host="127.0.0.1", port=8000, reload=True)
