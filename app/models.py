from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name_fa = Column(String(255), nullable=False, index=True)
    name_en = Column(String(255), nullable=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    condition = Column(String(50), default="نو")  # "نو" or "استوک"
    image_url = Column(String(500), nullable=True)
    lowest_price = Column(Float, default=0.0)  # In Tomans
    previous_lowest_price = Column(Float, default=0.0)
    change_percent = Column(Float, default=0.0)
    lowest_store_name = Column(String(100), nullable=True)
    in_stock = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=utc_now, onupdate=utc_now)

    vendor_offers = relationship(
        "VendorOffer",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="VendorOffer.current_price.asc()"
    )
    price_history = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="PriceHistory.timestamp.asc()"
    )

    def calculate_metrics(self):
        """Recalculate lowest price strictly from IN-STOCK offers only."""
        in_stock_offers = [o for o in self.vendor_offers if o.in_stock and o.current_price and o.current_price > 0]
        
        if in_stock_offers:
            cheapest = min(in_stock_offers, key=lambda o: o.current_price)
            if self.lowest_price and self.lowest_price > 0 and self.lowest_price != cheapest.current_price:
                self.previous_lowest_price = self.lowest_price
                if self.previous_lowest_price > 0:
                    diff = cheapest.current_price - self.previous_lowest_price
                    self.change_percent = round((diff / self.previous_lowest_price) * 100, 2)
            elif not self.previous_lowest_price or self.previous_lowest_price == 0:
                self.previous_lowest_price = cheapest.current_price
                self.change_percent = 0.0

            self.lowest_price = cheapest.current_price
            self.lowest_store_name = cheapest.store_name
            self.in_stock = True
        else:
            self.in_stock = False
            self.lowest_price = 0.0
            self.lowest_store_name = "ناموجود در بازار"
            self.change_percent = 0.0

    def to_dict(self, include_history=False):
        # Strictly return in-stock offers with valid verified prices
        valid_offers = [o.to_dict() for o in self.vendor_offers if o.in_stock and o.current_price and o.current_price > 0]
        prices = [o["current_price"] for o in valid_offers]
        
        avg_price = round(sum(prices) / len(prices)) if prices else (self.lowest_price or 0)
        max_price = max(prices) if prices else (self.lowest_price or 0)
        min_price = min(prices) if prices else (self.lowest_price or 0)
        spread_amount = max_price - min_price if len(prices) > 1 else 0
        spread_percent = round((spread_amount / min_price) * 100, 1) if (min_price > 0 and len(prices) > 1) else 0

        data = {
            "id": self.id,
            "name_fa": self.name_fa,
            "name_en": self.name_en or "",
            "category": self.category,
            "brand": self.brand,
            "condition": self.condition or "نو",
            "image_url": self.image_url or "",
            "lowest_price": self.lowest_price,
            "previous_lowest_price": self.previous_lowest_price,
            "change_percent": self.change_percent,
            "lowest_store_name": self.lowest_store_name or "",
            "in_stock": self.in_stock,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "offers_count": len(valid_offers),
            "vendor_offers": valid_offers,
            "average_price": avg_price,
            "max_price": max_price,
            "price_spread": spread_amount,
            "price_spread_percent": spread_percent
        }
        if include_history:
            data["price_history"] = [h.to_dict() for h in self.price_history]
        return data


class VendorOffer(Base):
    __tablename__ = "vendor_offers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    store_name = Column(String(100), nullable=False)
    product_url = Column(String(1000), nullable=False)
    dkp_or_sku = Column(String(100), nullable=True)
    current_price = Column(Float, default=0.0)  # Always normalized to Tomans
    previous_price = Column(Float, default=0.0)
    in_stock = Column(Boolean, default=True)
    currency_unit = Column(String(20), default="toman")  # "toman" or "rial"
    custom_css_selector = Column(String(255), nullable=True)
    last_checked = Column(DateTime, default=utc_now)
    last_status = Column(String(255), default="در انتظار پایش")

    product = relationship("Product", back_populates="vendor_offers")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "store_name": self.store_name,
            "product_url": self.product_url,
            "dkp_or_sku": self.dkp_or_sku or "",
            "current_price": self.current_price,
            "previous_price": self.previous_price,
            "in_stock": self.in_stock,
            "currency_unit": self.currency_unit,
            "custom_css_selector": self.custom_css_selector or "",
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_status": self.last_status or ""
        }


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    lowest_price = Column(Float, nullable=False)  # in Tomans
    store_name = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=utc_now, index=True)

    product = relationship("Product", back_populates="price_history")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "lowest_price": self.lowest_price,
            "store_name": self.store_name or "",
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
