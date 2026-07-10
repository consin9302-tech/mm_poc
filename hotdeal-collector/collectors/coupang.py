import hmac
import hashlib
import requests
import os
from time import gmtime, strftime
from collectors.base import BaseCollector

class CoupangPartnersClient(BaseCollector):
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

        # GMT 시각 문자열 생성
        datetime_gmt = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'
        message = datetime_gmt + method + path + query_string
        
        signature = hmac.new(
            bytes(self.secret_key, "utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        auth_header = (
            f"CEA algorithm=HmacSHA256, "
            f"access-key={self.access_key}, "
            f"signed-date={datetime_gmt}, "
            f"signature={signature}"
        )
        return auth_header, datetime_gmt

    def get_goldbox_products(self) -> list:
        """
        골드박스 상품 조회 API 호출
        """
        path = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/goldbox"
        url = self.base_url + path
        
        try:
            auth_header, signed_date = self._generate_auth_header("GET", path)
            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[Error] API request failed with status code {response.status_code}")
                print(response.text)
                return []
                
            res_data = response.json()
            
            if res_data.get("rCode") != "0":
                print(f"[Error] Coupang API returned error code {res_data.get('rCode')}: {res_data.get('rMessage')}")
                return []
                
            raw_products = res_data.get("data", [])
            parsed_products = []
            
            for item in raw_products:
                parsed_products.append({
                    "product_id": str(item.get("productId")),
                    "title": item.get("productName"),
                    "image_url": item.get("productImage"),
                    "original_url": item.get("productUrl"),
                    "price": int(item.get("productPrice", 0)),
                    "discount_rate": float(item.get("discountRate", 0))
                })
                
            return parsed_products

        except Exception as e:
            print(f"[Exception] Failed to collect Goldbox products: {e}")
            return []

    def collect(self) -> list:
        """
        BaseCollector 인터페이스 구현
        """
        return self.get_goldbox_products()
