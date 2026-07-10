import unittest
from collectors import (
    CoupangPartnersClient,
    NaverShoppingConnectClient,
    TossShoppingShareLinkClient,
    BaseCollector
)

class TestCollectorsStructure(unittest.TestCase):
    def test_client_instantiation(self):
        # 각 클라이언트가 정상적으로 생성되고 BaseCollector를 상속받는지 확인
        coupang_client = CoupangPartnersClient(access_key="test", secret_key="test")
        naver_client = NaverShoppingConnectClient(client_id="test", client_secret="test")
        toss_client = TossShoppingShareLinkClient(api_key="test")

        self.assertIsInstance(coupang_client, BaseCollector)
        self.assertIsInstance(naver_client, BaseCollector)
        self.assertIsInstance(toss_client, BaseCollector)

    def test_naver_collector_stub(self):
        # 네이버 스텁 수집기가 표준 데이터를 형식에 맞춰 반환하는지 테스트
        naver_client = NaverShoppingConnectClient()
        products = naver_client.collect()
        
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        
        for p in products:
            self.assertIn("product_id", p)
            self.assertIn("title", p)
            self.assertIn("image_url", p)
            self.assertIn("original_url", p)
            self.assertIn("price", p)
            self.assertIn("discount_rate", p)
            self.assertIsInstance(p["price"], int)
            self.assertIsInstance(p["discount_rate"], float)

    def test_toss_collector_stub(self):
        # 토스 스텁 수집기가 표준 데이터를 형식에 맞춰 반환하는지 테스트
        toss_client = TossShoppingShareLinkClient()
        products = toss_client.collect()
        
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        
        for p in products:
            self.assertIn("product_id", p)
            self.assertIn("title", p)
            self.assertIn("image_url", p)
            self.assertIn("original_url", p)
            self.assertIn("price", p)
            self.assertIn("discount_rate", p)
            self.assertIsInstance(p["price"], int)
            self.assertIsInstance(p["discount_rate"], float)

if __name__ == "__main__":
    unittest.main()
