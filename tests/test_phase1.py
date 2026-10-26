import pytest
from app.database import Base, SessionLocal, engine
from app.models import Product, VendorOffer, PriceHistory, AppSetting
from app.seed import seed_database

def test_database_initialization_and_seeding():
    # Force reseed database
    count = seed_database(force_reseed=True)
    assert count >= 20, f"Expected at least 20 seeded products, got {count}"

    db = SessionLocal()
    try:
        products = db.query(Product).all()
        assert len(products) >= 20

        # Check vendor offers
        offers = db.query(VendorOffer).all()
        assert len(offers) >= 40, f"Expected at least 40 vendor offers, got {len(offers)}"

        # Check price history
        history = db.query(PriceHistory).all()
        assert len(history) >= 20 * 7, f"Expected at least 140 history entries, got {len(history)}"

        # Verify Iranian stores exist in offers
        stores = {o.store_name for o in offers}
        assert "دیجیکالا" in stores
        assert "اگزو گیم" in stores
        assert "پیسی ماد" in stores
        assert "کارما آیتی" in stores
        assert "ام‌آیتی" in stores
        assert "لیون کامپیوتر" in stores
        assert "تاپ رایان" in stores

        # Verify categories & brands
        categories = {p.category for p in products}
        assert "پردازنده" in categories
        assert "کارت گرافیک" in categories
        assert "کولینگ و دیپکول" in categories
        assert "موس و کیبورد گیمینگ" in categories
        assert "لپتاپ نو و استوک" in categories

        brands = {p.brand for p in products}
        assert "DeepCool" in brands
        assert "Bloody" in brands
        assert "Razer" in brands
        assert "ASUS ROG" in brands
        assert "Intel" in brands
        assert "AMD" in brands
        assert "MSI" in brands

        # Check product calculation logic
        first_product = products[0]
        assert first_product.lowest_price > 0
        assert first_product.lowest_store_name != ""
        dict_rep = first_product.to_dict(include_history=True)
        assert "price_spread" in dict_rep
        assert "average_price" in dict_rep
        assert len(dict_rep["vendor_offers"]) > 0
        assert len(dict_rep["price_history"]) >= 8

        # Check settings
        tether_setting = db.query(AppSetting).filter_by(key="tether_irt_rate").first()
        assert tether_setting is not None
        assert int(tether_setting.value) > 50000

        print(f"Phase 1 Verification Passed: {len(products)} products, {len(offers)} offers, {len(history)} history entries.")
    finally:
        db.close()
