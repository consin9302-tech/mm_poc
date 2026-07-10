import os
import requests
from collectors.base import BaseCollector

class NaverShoppingConnectClient(BaseCollector):
    """
    네이버 쇼핑커넥트 API 연동 클라이언트 (2단계 확장 예정)
    """
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("NAVER_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("NAVER_CLIENT_SECRET")
        # 네이버 쇼핑커넥트 API 엔드포인트 설정 예정
        self.base_url = "https://openapi.naver.com" 

    def collect(self) -> list:
        """
        네이버 쇼핑커넥트 API를 호출하여 특가 상품 정보를 수집합니다.
        (현재는 POC 검증을 위한 스텁 데이터를 반환합니다)
        """
        print("-> 네이버 쇼핑커넥트 API 호출 시도 (현재는 Mock 데이터 반환)...")
        
        # 실제 API 호출 및 인증 예시 코드 주석
        """
        path = "/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        # ...
        """

        # 예상되는 리턴 표준 형식 데이터 스텁
        mock_products = [
            {
                "product_id": "naver_90001",
                "title": "[네이버특가] 신라면 20봉 묶음 무료배송",
                "image_url": "https://shopping-phinf.pstatic.net/main_...jpg",
                "original_url": "https://search.shopping.naver.com/catalog/...",
                "price": 14500,
                "discount_rate": 15.0
            },
            {
                "product_id": "naver_90002",
                "title": "[쇼핑페스타] 크리넥스 안심 3겹 화장지 30롤 x 2팩",
                "image_url": "https://shopping-phinf.pstatic.net/main_...jpg",
                "original_url": "https://search.shopping.naver.com/catalog/...",
                "price": 28900,
                "discount_rate": 25.0 # 20% 이상이므로 핫딜 선정 조건 충족
            }
        ]
        return mock_products
