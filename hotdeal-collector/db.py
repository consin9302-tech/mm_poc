import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# 데이터베이스 연결 설정
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///hotdeal.db")

# SQLite의 경우 동시성 및 다중 스레드 접속 에러 방지를 위해 connect_args 설정 추가
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False, index=True)  # 'coupang', 'naver', 'toss'
    product_id = Column(String, nullable=False, index=True)  # 플랫폼 상품 ID
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    original_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # 가격 변경 이력과의 관계 정의
    price_histories = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    observed_at = Column(DateTime, default=datetime.now)
    price = Column(Integer, nullable=False)  # 최종 판매 가격
    discount_rate = Column(Float, nullable=True)  # 할인율

    product = relationship("Product", back_populates="price_histories")


def init_db():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)


def save_or_update_product(session, platform, product_id, title, image_url, original_url, price, discount_rate):
    """
    상품 정보를 저장하거나 업데이트하고, 가격 변경이 있을 경우 이력을 기록합니다.
    
    Returns:
        tuple: (Product 객체, 가격 변동 여부(bool), 이전 가격(int/None), 현재 가격(int))
    """
    # 1. 기존 상품 조회
    product = session.query(Product).filter(
        Product.platform == platform,
        Product.product_id == product_id
    ).first()

    if not product:
        # 신규 상품 생성
        product = Product(
            platform=platform,
            product_id=product_id,
            title=title,
            image_url=image_url,
            original_url=original_url
        )
        session.add(product)
        session.flush()  # ID 확보를 위해 flush 실행
        
        # 최초 가격 이력 추가
        history = PriceHistory(
            product_id=product.id,
            price=price,
            discount_rate=discount_rate
        )
        session.add(history)
        return product, True, None, price

    # 2. 기존 상품이 존재할 경우, 최신 가격 확인
    latest_history = session.query(PriceHistory).filter(
        PriceHistory.product_id == product.id
    ).order_by(PriceHistory.observed_at.desc()).first()

    is_price_changed = False
    previous_price = None

    if not latest_history:
        # 이력이 없는 경우 추가
        history = PriceHistory(
            product_id=product.id,
            price=price,
            discount_rate=discount_rate
        )
        session.add(history)
        is_price_changed = True
    elif latest_history.price != price:
        # 가격 변동이 발생한 경우 새 이력 추가
        previous_price = latest_history.price
        history = PriceHistory(
            product_id=product.id,
            price=price,
            discount_rate=discount_rate
        )
        session.add(history)
        is_price_changed = True

    return product, is_price_changed, previous_price, price
