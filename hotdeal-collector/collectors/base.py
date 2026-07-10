from abc import ABC, abstractmethod

class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> list:
        """
        플랫폼별 상품 정보를 수집하여 표준 포맷으로 반환합니다.
        
        Returns:
            list: 아래 구조를 가지는 상품 정보 딕셔너리 리스트
                {
                    "product_id": str,
                    "title": str,
                    "image_url": str,
                    "original_url": str,
                    "price": int,
                    "discount_rate": float
                }
        """
        pass
