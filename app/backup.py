import os
import csv
import io
import json
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import Product, VendorOffer, PriceHistory, AppSetting
from app.seed import seed_database

def export_full_backup_json(db: Session = None) -> dict:
    """Generate complete JSON export of entire database."""
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        products = db.query(Product).all()
        offers = db.query(VendorOffer).all()
        history = db.query(PriceHistory).all()
        settings = db.query(AppSetting).all()

        data = {
            "metadata": {
                "app": "AuraTech Tracker",
                "version": "1.0.0",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "products_count": len(products),
                "offers_count": len(offers),
                "history_count": len(history)
            },
            "products": [
                {
                    "id": p.id,
                    "name_fa": p.name_fa,
                    "name_en": p.name_en,
                    "category": p.category,
                    "brand": p.brand,
                    "condition": p.condition,
                    "image_url": p.image_url,
                    "lowest_price": p.lowest_price,
                    "previous_lowest_price": p.previous_lowest_price,
                    "change_percent": p.change_percent,
                    "lowest_store_name": p.lowest_store_name,
                    "in_stock": p.in_stock,
                    "last_updated": p.last_updated.isoformat() if p.last_updated else None
                }
                for p in products
            ],
            "vendor_offers": [
                {
                    "id": o.id,
                    "product_id": o.product_id,
                    "store_name": o.store_name,
                    "product_url": o.product_url,
                    "dkp_or_sku": o.dkp_or_sku,
                    "current_price": o.current_price,
                    "previous_price": o.previous_price,
                    "in_stock": o.in_stock,
                    "currency_unit": o.currency_unit,
                    "custom_css_selector": o.custom_css_selector,
                    "last_checked": o.last_checked.isoformat() if o.last_checked else None,
                    "last_status": o.last_status
                }
                for o in offers
            ],
            "price_history": [
                {
                    "id": h.id,
                    "product_id": h.product_id,
                    "lowest_price": h.lowest_price,
                    "store_name": h.store_name,
                    "timestamp": h.timestamp.isoformat() if h.timestamp else None
                }
                for h in history
            ],
            "app_settings": [
                {
                    "key": s.key,
                    "value": s.value,
                    "updated_at": s.updated_at.isoformat() if s.updated_at else None
                }
                for s in settings
            ]
        }
        return data
    finally:
        if own_session:
            db.close()


def import_full_backup_json(payload: dict, mode: str = "replace", db: Session = None) -> dict:
    """Restore database from JSON payload ('replace' or 'merge')."""
    if not isinstance(payload, dict) or "products" not in payload:
        return {"success": False, "error": "فرمت فایل پشتیبان معتبر نیست."}

    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        # Ensure schema
        Base.metadata.create_all(bind=engine)

        if mode == "replace":
            db.query(PriceHistory).delete()
            db.query(VendorOffer).delete()
            db.query(Product).delete()
            db.query(AppSetting).delete()
            db.commit()

        # Restore products
        id_map = {}
        for p_data in payload.get("products", []):
            last_up = None
            if p_data.get("last_updated"):
                try:
                    last_up = datetime.fromisoformat(p_data["last_updated"])
                except Exception:
                    last_up = datetime.now(timezone.utc)

            new_prod = Product(
                name_fa=p_data.get("name_fa", ""),
                name_en=p_data.get("name_en", ""),
                category=p_data.get("category", "سایر"),
                brand=p_data.get("brand", "نامشخص"),
                condition=p_data.get("condition", "نو"),
                image_url=p_data.get("image_url", ""),
                lowest_price=float(p_data.get("lowest_price", 0)),
                previous_lowest_price=float(p_data.get("previous_lowest_price", 0)),
                change_percent=float(p_data.get("change_percent", 0.0)),
                lowest_store_name=p_data.get("lowest_store_name", ""),
                in_stock=bool(p_data.get("in_stock", True)),
                last_updated=last_up
            )
            db.add(new_prod)
            db.flush()
            if "id" in p_data:
                id_map[p_data["id"]] = new_prod.id

        # Restore vendor offers
        for o_data in payload.get("vendor_offers", []):
            orig_pid = o_data.get("product_id")
            target_pid = id_map.get(orig_pid, orig_pid)
            if not target_pid:
                continue

            last_chk = None
            if o_data.get("last_checked"):
                try:
                    last_chk = datetime.fromisoformat(o_data["last_checked"])
                except Exception:
                    last_chk = datetime.now(timezone.utc)

            new_offer = VendorOffer(
                product_id=target_pid,
                store_name=o_data.get("store_name", ""),
                product_url=o_data.get("product_url", ""),
                dkp_or_sku=o_data.get("dkp_or_sku", ""),
                current_price=float(o_data.get("current_price", 0)),
                previous_price=float(o_data.get("previous_price", 0)),
                in_stock=bool(o_data.get("in_stock", True)),
                currency_unit=o_data.get("currency_unit", "toman"),
                custom_css_selector=o_data.get("custom_css_selector", ""),
                last_checked=last_chk,
                last_status=o_data.get("last_status", "بازیابی شده")
            )
            db.add(new_offer)

        # Restore price history
        for h_data in payload.get("price_history", []):
            orig_pid = h_data.get("product_id")
            target_pid = id_map.get(orig_pid, orig_pid)
            if not target_pid:
                continue

            t_stamp = None
            if h_data.get("timestamp"):
                try:
                    t_stamp = datetime.fromisoformat(h_data["timestamp"])
                except Exception:
                    t_stamp = datetime.now(timezone.utc)

            hist = PriceHistory(
                product_id=target_pid,
                lowest_price=float(h_data.get("lowest_price", 0)),
                store_name=h_data.get("store_name", ""),
                timestamp=t_stamp
            )
            db.add(hist)

        # Restore settings
        for s_data in payload.get("app_settings", []):
            key = s_data.get("key")
            if not key:
                continue
            exist_s = db.query(AppSetting).filter_by(key=key).first()
            if exist_s:
                exist_s.value = s_data.get("value", "")
            else:
                db.add(AppSetting(key=key, value=s_data.get("value", "")))

        db.commit()

        # Recalculate metrics for all products
        all_prods = db.query(Product).all()
        for p in all_prods:
            p.calculate_metrics()
        db.commit()

        return {
            "success": True,
            "restored_products": len(payload.get("products", [])),
            "restored_offers": len(payload.get("vendor_offers", [])),
            "message": f"اطلاعات با موفقیت بازیابی شدند ({len(payload.get('products', []))} کالا)."
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"خطا در بازیابی دیتابیس: {str(e)}"}
    finally:
        if own_session:
            db.close()


def export_products_csv(db: Session = None) -> str:
    """Generate CSV with UTF-8 BOM for Persian Microsoft Excel compatibility."""
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        products = db.query(Product).all()
        output = io.StringIO()
        # Write UTF-8 BOM
        output.write("\ufeff")
        writer = csv.writer(output)

        writer.writerow([
            "شناسه",
            "نام کالا (فارسی)",
            "نام کالا (انگلیسی)",
            "دسته‌بندی",
            "برند",
            "وضعیت",
            "کف قیمت (تومان)",
            "ارزان‌ترین فروشگاه",
            "میانگین قیمت بازار (تومان)",
            "تعداد فروشگاه‌ها",
            "وضعیت موجودی",
            "تاریخ آخرین پایش",
            "لینک‌های فروشگاه‌ها"
        ])

        for p in products:
            p_dict = p.to_dict()
            offers_links = " | ".join([f"{o['store_name']}: {o['product_url']}" for o in p_dict["vendor_offers"]])
            writer.writerow([
                p.id,
                p.name_fa,
                p.name_en or "",
                p.category,
                p.brand,
                p.condition or "نو",
                f"{int(p.lowest_price):,}" if p.lowest_price else "0",
                p.lowest_store_name or "",
                f"{int(p_dict['average_price']):,}" if p_dict.get("average_price") else "0",
                p_dict["offers_count"],
                "موجود" if p.in_stock else "ناموجود",
                p.last_updated.strftime("%Y-%m-%d %H:%M") if p.last_updated else "",
                offers_links
            ])

        return output.getvalue()
    finally:
        if own_session:
            db.close()


def get_gist_credentials(db: Session = None):
    """Retrieve GitHub token and gist ID from settings or environment."""
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True
    try:
        token_setting = db.query(AppSetting).filter_by(key="github_backup_token").first()
        gist_setting = db.query(AppSetting).filter_by(key="github_gist_id").first()
        
        token = (token_setting.value if token_setting and token_setting.value else None) or os.getenv("GITHUB_BACKUP_TOKEN")
        gist_id = (gist_setting.value if gist_setting and gist_setting.value else None) or os.getenv("GITHUB_GIST_ID")
        return token, gist_id
    finally:
        if own_session:
            db.close()


async def sync_to_github_gist(token: str = None, gist_id: str = None, db: Session = None) -> dict:
    """Push complete DB backup JSON to GitHub Gist."""
    if not token or not gist_id:
        env_token, env_gist_id = get_gist_credentials(db)
        token = token or env_token
        gist_id = gist_id or env_gist_id

    if not token:
        return {"success": False, "error": "توکن گیت‌هاب (GITHUB_BACKUP_TOKEN) تنظیم نشده است."}

    backup_data = export_full_backup_json(db)
    backup_json_str = json.dumps(backup_data, ensure_ascii=False, indent=2)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
            if gist_id:
                # Update existing Gist
                url = f"https://api.github.com/gists/{gist_id}"
                body = {
                    "description": "AuraTech Tracker Automated Database Backup",
                    "files": {
                        "auratech_backup.json": {
                            "content": backup_json_str
                        }
                    }
                }
                res = await client.patch(url, json=body)
                if res.status_code == 200:
                    return {
                        "success": True,
                        "gist_id": gist_id,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "message": "همگام‌سازی ابری گیت‌هاب با موفقیت انجام شد."
                    }
                else:
                    return {"success": False, "error": f"پاسخ گیت‌هاب: {res.status_code} - {res.text[:100]}"}
            else:
                # Create a new secret Gist
                url = "https://api.github.com/gists"
                body = {
                    "description": "AuraTech Tracker Automated Database Backup",
                    "public": False,
                    "files": {
                        "auratech_backup.json": {
                            "content": backup_json_str
                        }
                    }
                }
                res = await client.post(url, json=body)
                if res.status_code in [200, 201]:
                    new_gist = res.json()
                    new_id = new_gist.get("id")
                    # Save to DB setting
                    own_s = False
                    if db is None:
                        db = SessionLocal()
                        own_s = True
                    try:
                        g_sett = db.query(AppSetting).filter_by(key="github_gist_id").first()
                        if g_sett:
                            g_sett.value = new_id
                        else:
                            db.add(AppSetting(key="github_gist_id", value=new_id))
                        db.commit()
                    finally:
                        if own_s:
                            db.close()

                    return {
                        "success": True,
                        "gist_id": new_id,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "message": f"گست ابری جدید ایجاد و بک‌آپ ذخیره شد (شناسه: {new_id})."
                    }
                else:
                    return {"success": False, "error": f"خطا در ایجاد گست: {res.status_code} - {res.text[:100]}"}
    except Exception as e:
        return {"success": False, "error": f"خطای ارتباط با سرور گیت‌هاب: {str(e)}"}


async def restore_from_github_gist(token: str = None, gist_id: str = None, db: Session = None) -> dict:
    """Pull backup JSON from GitHub Gist and restore database."""
    if not token or not gist_id:
        env_token, env_gist_id = get_gist_credentials(db)
        token = token or env_token
        gist_id = gist_id or env_gist_id

    if not gist_id:
        return {"success": False, "error": "شناسه گست (GITHUB_GIST_ID) مشخص نشده است."}

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        url = f"https://api.github.com/gists/{gist_id}"
        async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                gist_data = res.json()
                files = gist_data.get("files", {})
                backup_file = files.get("auratech_backup.json")
                if not backup_file or "content" not in backup_file:
                    return {"success": False, "error": "فایل auratech_backup.json در این گست یافت نشد."}

                payload = json.loads(backup_file["content"])
                return import_full_backup_json(payload, mode="replace", db=db)
            else:
                return {"success": False, "error": f"گست یافت نشد: {res.status_code}"}
    except Exception as e:
        return {"success": False, "error": f"خطا در فراخوانی گست ابری: {str(e)}"}


async def check_and_auto_restore_on_startup():
    """Run at FastAPI startup: if database is freshly initialized or empty, try Gist restore, else seed initial data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        prod_count = db.query(Product).count()
        if prod_count > 0:
            return f"پایگاه داده دارای {prod_count} کالا می‌باشد (بدون نیاز به بازگردانی)."

        # Try Gist cloud restore first if credentials exist
        token, gist_id = get_gist_credentials(db)
        if gist_id:
            restore_res = await restore_from_github_gist(token=token, gist_id=gist_id, db=db)
            if restore_res.get("success"):
                return f"اطلاعات به طور خودکار از گست ابری بازیابی شد ({restore_res.get('restored_products')} کالا)."

        # Fallback to initial rich seed data
        count = seed_database(force_reseed=False)
        return f"دیتابیس با {count} کالای پیش‌فرض بازار ایران مقداردهی اولیه شد."
    finally:
        db.close()
