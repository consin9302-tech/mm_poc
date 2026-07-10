import hmac
import hashlib
import requests
import os
from time import gmtime, strftime

class CoupangPartnersClient:
    def __init__(self, access_key=None, secret_key=None):
        self.access_key = access_key or os.getenv("COUPANG_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("COUPANG_SECRET_KEY")
        self.base_url = "https://api-gateway.coupang.com"

    def _generate_auth_header(self, method, path, query_string=""):
        """
        쿠팡 파트너스 API 인증을 위한 HMAC-SHA256 Authorization 헤더 생성
        """
        if not self.access_key or not self.secret_key:
            raise ValueError("Coupang Access Key and Secret Key must be provided.")

        # GMT 시각 문자열 생성 (예: 260709T134538Z)
        datetime_gmt = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'
        
        # 메시지 조합 (메서드 + 경로 + 쿼리 스트링)
        # 쿼리가 없으면 빈 값 사용
        message = datetime_gmt + method + path + query_string
        
        # HMAC SHA256 서명 생성
        signature = hmac.new(
            bytes(self.secret_key, "utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        # 헤더 포맷팅
        auth_header = (
            f"CEA algorithm=HmacSHA256, "
            f"access-key={self.access_key}, "
            f"signed-date={datetime_gmt}, "
            f"signature={signature}"
        )
        return auth_header, datetime_gmt

    def get_goldbox_products(self):
        """
        골드박스 상품 조회 API 호출
        
        Returns:
            list: 상품 정보 딕셔너리 리스트
        """
        path = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/goldbox"
        url = self.base_url + path
        
        try:
            # 1. 인증 헤더 생성
            auth_header, signed_date = self._generate_auth_header("GET", path)
            
            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json"
            }
            
            # 2. API 요청 전송
            response = requests.get(url, headers=headers, timeout=10)
            
            # 응답 상태 확인
            if response.status_code != 200:
                print(f"[Error] API request failed with status code {response.status_code}")
                print(response.text)
                return []
                
            res_data = response.json()
            
            # 쿠팡 API 응답 코드 검증
            if res_data.get("rCode") != "0":
                print(f"[Error] Coupang API returned error code {res_data.get('rCode')}: {res_data.get('rMessage')}")
                return []
                
            # 상품 데이터 리스트 파싱 및 표준화
            raw_products = res_data.get("data", [])
            parsed_products = []
            
            for item in raw_products:
                parsed_products.append({
                    "product_id": str(item.get("productId")),
                    "title": item.get("productName"),
                    "image_url": item.get("productImage"),
                    "original_url": item.get("productUrl"),
                    "price": int(item.get("productPrice", 0)),
                    # 할인율 계산 (할인율 정보가 없을 시 원래가격 대비 할인율 계산 가능)
                    "discount_rate": float(item.get("discountRate", 0))
                })
                
            return parsed_products

        except Exception as e:
            print(f"[Exception] Failed to collect Goldbox products: {e}")
            return []
