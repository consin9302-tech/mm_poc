import os
import requests
from collectors.base import BaseCollector

class TossShoppingShareLinkClient(BaseCollector):
    """
    토스쇼핑 쉐어링크 API 연동 클라이언트 (2단계 확장 예정)
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("TOSS_SHARE_API_KEY")
        # 토스쇼핑 API 엔드포인트 설정 예정
        self.base_url = "https://api.toss.im" 

    def collect(self) -> list:
        """
        토스쇼핑 API를 호출하여 특가 상품 정보를 수집합니다.
        (현재는 POC 검증을 위한 스텁 데이터를 반환합니다)
        """
        print("-> 토스쇼핑 쉐어링크 API 호출 시도 (현재는 Mock 데이터 반환)...")
        
        # 예상되는 리턴 표준 형식 데이터 스텁
        mock_products = [
            {
                "product_id": "toss_80001",
                "title": "[토스특가] 맛있는 닭가슴살 100g 10팩 골라담기",
                "image_url": "https://static.toss.im/assets/...png",
                "original_url": "https://toss.im/share-link/...",
                "price": 9900,
                "discount_rate": 30.0 # 20% 이상이므로 핫딜 선정 조건 충족
            },
            {
                "product_id": "toss_80002",
                "title": "[한정수량] 국산 KF94 마스크 100매입 황사방역",
                "image_url": "https://static.toss.im/assets/...png",
                "original_url": "https://toss.im/share-link/...",
                "price": 18000,
                "discount_rate": 10.0
            }
        ]
        return mock_products
