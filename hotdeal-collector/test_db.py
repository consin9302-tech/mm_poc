import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base, Product, PriceHistory, save_or_update_product

class TestDatabaseLogic(unittest.TestCase):
    def setUp(self):
        # 테스트용 인메모리 SQLite DB 생성
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_save_new_product(self):
        # 1. 신규 상품 저장
        platform = "coupang"
        product_id = "12345"
        title = "테스트 상품"
        image_url = "http://example.com/image.jpg"
        original_url = "http://example.com/product"
        price = 10000
        discount_rate = 10.0

        product, is_changed, prev_price, curr_price = save_or_update_product(
            self.session, platform, product_id, title, image_url, original_url, price, discount_rate
        )
        self.session.commit()

        # 2. 결과 검증
        self.assertIsNotNone(product.id)
        self.assertTrue(is_changed)
        self.assertIsNone(prev_price)
        self.assertEqual(curr_price, price)

        # DB 조회 검증
        db_product = self.session.query(Product).filter_by(id=product.id).first()
        self.assertEqual(db_product.title, title)
        self.assertEqual(len(db_product.price_histories), 1)
        self.assertEqual(db_product.price_histories[0].price, price)

    def test_update_product_same_price(self):
        # 1. 상품 등록
        platform = "coupang"
        product_id = "12345"
        title = "테스트 상품"
        image_url = "http://example.com/image.jpg"
        original_url = "http://example.com/product"
        price = 10000
        discount_rate = 10.0

        save_or_update_product(
            self.session, platform, product_id, title, image_url, original_url, price, discount_rate
        )
        self.session.commit()

        # 2. 동일한 가격으로 다시 업데이트 시도
        product, is_changed, prev_price, curr_price = save_or_update_product(
            self.session, platform, product_id, title, image_url, original_url, price, discount_rate
        )
        self.session.commit()

        # 3. 결과 검증 (변동 사항이 없어야 함)
        self.assertFalse(is_changed)
        self.assertEqual(curr_price, price)
        self.assertEqual(len(product.price_histories), 1)

    def test_update_product_different_price(self):
        # 1. 상품 등록
        platform = "coupang"
        product_id = "12345"
        title = "테스트 상품"
        image_url = "http://example.com/image.jpg"
        original_url = "http://example.com/product"
        price = 10000
        discount_rate = 10.0

        save_or_update_product(
            self.session, platform, product_id, title, image_url, original_url, price, discount_rate
        )
        self.session.commit()

        # 2. 다른 가격으로 업데이트 (가격 하락)
        new_price = 8000
        new_discount_rate = 20.0
        product, is_changed, prev_price, curr_price = save_or_update_product(
            self.session, platform, product_id, title, image_url, original_url, new_price, new_discount_rate
        )
        self.session.commit()

        # 3. 결과 검증 (가격 변동이 참이고, 이전 가격이 10000이어야 함)
        self.assertTrue(is_changed)
        self.assertEqual(prev_price, 10000)
        self.assertEqual(curr_price, new_price)
        self.assertEqual(len(product.price_histories), 2)
        
        # 최신 이력 확인
        histories = sorted(product.price_histories, key=lambda h: h.observed_at)
        self.assertEqual(histories[0].price, 10000)
        self.assertEqual(histories[1].price, 8000)

if __name__ == "__main__":
    unittest.main()
