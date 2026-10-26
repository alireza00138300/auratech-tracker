import pytest
from app.database import SessionLocal, Base, engine
from app.models import Product, VendorOffer, PriceHistory
from app.seed import seed_database
from app.backup import (
    export_full_backup_json,
    import_full_backup_json,
    export_products_csv,
    check_and_auto_restore_on_startup
)

def test_export_import_json_backup_cycle():
    # Seed DB
    seed_database(force_reseed=True)
    db = SessionLocal()

    try:
        initial_products_count = db.query(Product).count()
        initial_offers_count = db.query(VendorOffer).count()
        assert initial_products_count >= 20
        assert initial_offers_count >= 40

        # Export full JSON backup
        backup_data = export_full_backup_json(db)
        assert "metadata" in backup_data
        assert len(backup_data["products"]) == initial_products_count
        assert len(backup_data["vendor_offers"]) == initial_offers_count

        # Wipe a specific record
        target_product = db.query(Product).filter(Product.name_fa.like("%13400F%")).first()
        assert target_product is not None
        target_name = target_product.name_fa
        db.delete(target_product)
        db.commit()

        # Verify deletion
        assert db.query(Product).count() == initial_products_count - 1

        # Restore from backup
        restore_result = import_full_backup_json(backup_data, mode="replace", db=db)
        assert restore_result["success"] is True

        # Verify full restoration and data integrity
        restored_products_count = db.query(Product).count()
        restored_offers_count = db.query(VendorOffer).count()
        assert restored_products_count == initial_products_count
        assert restored_offers_count == initial_offers_count

        restored_item = db.query(Product).filter_by(name_fa=target_name).first()
        assert restored_item is not None
        assert restored_item.lowest_price > 0
        assert len(restored_item.vendor_offers) > 0
    finally:
        db.close()


def test_export_products_csv_utf8_bom():
    db = SessionLocal()
    try:
        csv_str = export_products_csv(db)
        # Check UTF-8 BOM
        assert csv_str.startswith("\ufeff")
        assert "شناسه,نام کالا (فارسی)" in csv_str
        assert "کف قیمت (تومان)" in csv_str
        assert "دیجیکالا" in csv_str or "اگزو گیم" in csv_str
    finally:
        db.close()


@pytest.mark.anyio
async def test_startup_check_and_auto_restore():
    status = await check_and_auto_restore_on_startup()
    assert "پایگاه داده" in status or "کالا" in status
