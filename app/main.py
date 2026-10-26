import os
import json
import time
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import get_db, SessionLocal, engine, Base
from app.models import Product, VendorOffer, PriceHistory, AppSetting
from app.scraper import scraper_engine, fetch_nobitex_tether, detect_store_name
from app.backup import (
    export_full_backup_json,
    import_full_backup_json,
    export_products_csv,
    sync_to_github_gist,
    restore_from_github_gist,
    check_and_auto_restore_on_startup,
    get_gist_credentials
)

scheduler = AsyncIOScheduler()

async def scheduled_scrape_task():
    """Background task executed every 20 minutes."""
    print(f"[{datetime.now()}] Starting scheduled multi-vendor scrape...")
    await run_full_scrape_pipeline()
    # Also refresh tether rate
    await refresh_tether_rate()

async def refresh_tether_rate():
    t_res = await fetch_nobitex_tether()
    db = SessionLocal()
    try:
        sett = db.query(AppSetting).filter_by(key="tether_irt_rate").first()
        if sett:
            sett.value = str(t_res.get("tether_toman", 98500))
        else:
            db.add(AppSetting(key="tether_irt_rate", value=str(t_res.get("tether_toman", 98500))))
        db.commit()
    finally:
        db.close()

async def run_full_scrape_pipeline(limit: Optional[int] = None) -> dict:
    start_time = time.time()
    db = SessionLocal()
    scraped_count = 0
    updated_products = 0

    try:
        query = db.query(VendorOffer)
        if limit:
            query = query.limit(limit)
        offers = query.all()
        products_to_recalc = set()

        sem = asyncio.Semaphore(8)

        async def scrape_single_offer(offer):
            nonlocal scraped_count
            async with sem:
                res = await scraper_engine.scrape_url(offer.product_url, offer.custom_css_selector)
                scraped_count += 1
                return offer, res

        tasks = [scrape_single_offer(o) for o in offers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for item in results:
            if isinstance(item, Exception):
                continue
            offer, res = item
            if res.get("success") and res.get("price", 0) > 0:
                new_price = res["price"]
                if offer.current_price != new_price:
                    offer.previous_price = offer.current_price
                    offer.current_price = new_price
                offer.in_stock = res.get("in_stock", True)
                offer.last_checked = datetime.now(timezone.utc)
                offer.last_status = f"{res.get('layer', 'پایش موفق')} - {datetime.now().strftime('%H:%M')}"
                products_to_recalc.add(offer.product_id)

        # Recalculate metrics for affected products
        for pid in products_to_recalc:
            prod = db.query(Product).filter_by(id=pid).first()
            if prod:
                old_lowest = prod.lowest_price
                prod.calculate_metrics()
                if old_lowest != prod.lowest_price:
                    # Save price history
                    hist = PriceHistory(
                        product_id=prod.id,
                        lowest_price=float(prod.lowest_price),
                        store_name=prod.lowest_store_name,
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.add(hist)
                    updated_products += 1

        # Update last scrape timestamp setting
        last_s = db.query(AppSetting).filter_by(key="last_scrape_time").first()
        now_iso = datetime.now(timezone.utc).isoformat()
        if last_s:
            last_s.value = now_iso
        else:
            db.add(AppSetting(key="last_scrape_time", value=now_iso))

        db.commit()

        # Check if auto GitHub Gist sync is enabled
        auto_sync = db.query(AppSetting).filter_by(key="auto_sync_gist").first()
        if auto_sync and auto_sync.value.lower() == "true":
            await sync_to_github_gist(db=db)

        elapsed = round(time.time() - start_time, 2)
        return {
            "success": True,
            "scraped_offers": scraped_count,
            "updated_products": updated_products,
            "elapsed_seconds": elapsed
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables, check auto-restore from cloud / seed
    status = await check_and_auto_restore_on_startup()
    print(f"AuraTech Startup: {status}")

    # Start APScheduler (Every 20 minutes)
    scheduler.add_job(scheduled_scrape_task, "interval", minutes=20, id="auratech_scrape_20m")
    scheduler.start()

    yield

    # Shutdown
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="AuraTech Tracker | سامانه پایش هوشمند بازار سخت‌افزار ایران",
    version="1.0.0",
    lifespan=lifespan
)

# Static & Template directories
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Pydantic Schemas ---
class OfferCreate(BaseModel):
    store_name: Optional[str] = None
    product_url: str
    custom_css_selector: Optional[str] = None
    current_price: Optional[float] = None
    currency_unit: Optional[str] = "toman"

class ProductCreate(BaseModel):
    name_fa: str
    name_en: Optional[str] = ""
    category: str
    brand: str
    condition: Optional[str] = "نو"
    image_url: Optional[str] = ""
    initial_offer: Optional[OfferCreate] = None

class ProductUpdate(BaseModel):
    name_fa: Optional[str] = None
    name_en: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = None
    image_url: Optional[str] = None

class TestUrlRequest(BaseModel):
    url: str
    custom_selector: Optional[str] = None

class SettingsUpdate(BaseModel):
    github_backup_token: Optional[str] = None
    github_gist_id: Optional[str] = None
    auto_sync_gist: Optional[str] = None
    quote_default_margin: Optional[str] = None
    quote_default_assembly_fee: Optional[str] = None
    quote_default_software_fee: Optional[str] = None


# --- Web Page Route ---
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


# --- API Routes: Products & Offers ---
@app.get("/api/products")
def get_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    store: Optional[str] = None,
    condition: Optional[str] = None,
    in_stock_only: Optional[bool] = False,
    sort_by: Optional[str] = "lowest_price_asc",
    discount_only: Optional[bool] = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category and category != "همه":
        query = query.filter(Product.category == category)
    if brand and brand != "همه":
        query = query.filter(Product.brand == brand)
    if condition and condition != "همه":
        query = query.filter(Product.condition == condition)
    if in_stock_only:
        query = query.filter(Product.in_stock == True)
    if discount_only:
        query = query.filter(Product.change_percent < 0)
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Product.name_fa.ilike(search_fmt)) |
            (Product.name_en.ilike(search_fmt)) |
            (Product.brand.ilike(search_fmt))
        )

    products = query.all()

    # Filter by store in memory if requested
    if store and store != "همه":
        filtered = []
        for p in products:
            if any(o.store_name == store for o in p.vendor_offers):
                filtered.append(p)
        products = filtered

    # Sort
    if sort_by == "lowest_price_asc":
        products.sort(key=lambda p: (not p.in_stock, p.lowest_price or float("inf")))
    elif sort_by == "lowest_price_desc":
        products.sort(key=lambda p: (p.lowest_price or 0), reverse=True)
    elif sort_by == "discount_desc":
        products.sort(key=lambda p: (p.change_percent or 0))
    elif sort_by == "name_asc":
        products.sort(key=lambda p: p.name_fa)

    # Extract all distinct categories, brands, stores for UI filters
    all_products = db.query(Product).all()
    categories = sorted(list({p.category for p in all_products if p.category}))
    brands = sorted(list({p.brand for p in all_products if p.brand}))
    all_offers = db.query(VendorOffer).all()
    stores = sorted(list({o.store_name for o in all_offers if o.store_name}))

    return {
        "total": len(products),
        "products": [p.to_dict(include_history=True) for p in products],
        "categories": categories,
        "brands": brands,
        "stores": stores
    }


@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="کالای مورد نظر یافت نشد.")
    return prod.to_dict(include_history=True)


@app.post("/api/products")
async def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    prod = Product(
        name_fa=payload.name_fa,
        name_en=payload.name_en or "",
        category=payload.category,
        brand=payload.brand,
        condition=payload.condition or "نو",
        image_url=payload.image_url or "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
        last_updated=datetime.now(timezone.utc)
    )
    db.add(prod)
    db.flush()

    if payload.initial_offer and payload.initial_offer.product_url:
        s_name = payload.initial_offer.store_name or detect_store_name(payload.initial_offer.product_url)
        price = payload.initial_offer.current_price
        
        # Scrape immediately if price not provided
        if not price or price <= 0:
            scrape_res = await scraper_engine.scrape_url(payload.initial_offer.product_url, payload.initial_offer.custom_css_selector)
            price = scrape_res.get("price", 0)

        offer = VendorOffer(
            product_id=prod.id,
            store_name=s_name,
            product_url=payload.initial_offer.product_url,
            current_price=float(price or 0),
            previous_price=float(price or 0),
            custom_css_selector=payload.initial_offer.custom_css_selector or "",
            in_stock=True,
            last_checked=datetime.now(timezone.utc),
            last_status="پایش اولیه موفق"
        )
        db.add(offer)
        db.flush()

    prod.calculate_metrics()
    # Save initial price history point
    if prod.lowest_price > 0:
        hist = PriceHistory(
            product_id=prod.id,
            lowest_price=float(prod.lowest_price),
            store_name=prod.lowest_store_name,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(hist)

    db.commit()
    return prod.to_dict(include_history=True)


@app.put("/api/products/{product_id}")
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="کالا یافت نشد.")

    if payload.name_fa is not None:
        prod.name_fa = payload.name_fa
    if payload.name_en is not None:
        prod.name_en = payload.name_en
    if payload.category is not None:
        prod.category = payload.category
    if payload.brand is not None:
        prod.brand = payload.brand
    if payload.condition is not None:
        prod.condition = payload.condition
    if payload.image_url is not None:
        prod.image_url = payload.image_url

    prod.last_updated = datetime.now(timezone.utc)
    db.commit()
    return prod.to_dict()


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="کالا یافت نشد.")
    db.delete(prod)
    db.commit()
    return {"success": True, "message": "کالا با موفقیت حذف شد."}


@app.post("/api/products/{product_id}/offers")
async def add_offer_to_product(product_id: int, payload: OfferCreate, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="کالا یافت نشد.")

    s_name = payload.store_name or detect_store_name(payload.product_url)
    price = payload.current_price
    in_stock = True
    last_status = "ثبت شده"

    if not price or price <= 0:
        res = await scraper_engine.scrape_url(payload.product_url, payload.custom_css_selector)
        if res.get("success") and res.get("price", 0) > 0:
            price = res["price"]
            in_stock = res.get("in_stock", True)
            last_status = res.get("layer", "پایش موفق")

    offer = VendorOffer(
        product_id=prod.id,
        store_name=s_name,
        product_url=payload.product_url,
        current_price=float(price or 0),
        previous_price=float(price or 0),
        in_stock=in_stock,
        custom_css_selector=payload.custom_css_selector or "",
        last_checked=datetime.now(timezone.utc),
        last_status=last_status
    )
    db.add(offer)
    db.flush()

    prod.calculate_metrics()
    db.commit()
    return prod.to_dict(include_history=True)


@app.delete("/api/offers/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(VendorOffer).filter(VendorOffer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="لینک فروشگاه یافت نشد.")

    pid = offer.product_id
    db.delete(offer)
    db.flush()

    prod = db.query(Product).filter(Product.id == pid).first()
    if prod:
        prod.calculate_metrics()
    db.commit()
    return {"success": True, "message": "لینک فروشگاه حذف شد."}


# --- API Routes: Scraper & Cron ---
@app.post("/api/scraper/test-url")
async def test_scraper_url(payload: TestUrlRequest):
    """Live preview price and title extracted from any Iranian store URL."""
    res = await scraper_engine.scrape_url(payload.url, payload.custom_selector)
    return res


@app.post("/api/scrape/run")
async def trigger_manual_scrape(limit: Optional[int] = None):
    """Manual 1-click trigger to scrape vendor offers."""
    res = await run_full_scrape_pipeline(limit=limit)
    return res


@app.get("/api/cron/trigger")
async def cron_trigger_keepalive(limit: Optional[int] = None):
    """Lightweight 20-min keep-alive and scrape trigger for cron-job.org / render."""
    res = await run_full_scrape_pipeline(limit=limit)
    return {
        "status": "ok",
        "message": "Cron keep-alive & scraper cycle completed successfully.",
        "result": res,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# --- API Routes: Market Overview & Tether ---
@app.get("/api/market-overview")
def get_market_overview(db: Session = Depends(get_db)):
    tether_sett = db.query(AppSetting).filter_by(key="tether_irt_rate").first()
    last_scrape_sett = db.query(AppSetting).filter_by(key="last_scrape_time").first()
    auto_sync_sett = db.query(AppSetting).filter_by(key="auto_sync_gist").first()

    token, gist_id = get_gist_credentials(db)
    has_cloud_sync = bool(token and (gist_id or auto_sync_sett and auto_sync_sett.value.lower() == "true"))

    products = db.query(Product).all()
    offers = db.query(VendorOffer).all()

    # Cheapest vendor leaderboard
    vendor_wins = {}
    for p in products:
        if p.lowest_store_name and p.in_stock:
            vendor_wins[p.lowest_store_name] = vendor_wins.get(p.lowest_store_name, 0) + 1

    cheapest_leaderboard = [
        {"store_name": k, "count": v}
        for k, v in sorted(vendor_wins.items(), key=lambda x: x[1], reverse=True)
    ]

    # Top price drops
    drops = [p.to_dict() for p in products if p.change_percent < 0 and p.in_stock]
    drops.sort(key=lambda x: x["change_percent"])

    return {
        "tether_toman": int(tether_sett.value) if tether_sett and tether_sett.value else 98500,
        "tether_source": "نوبیتکس (Nobitex Live)",
        "last_sync_time": last_scrape_sett.value if last_scrape_sett else datetime.now(timezone.utc).isoformat(),
        "total_products": len(products),
        "total_offers": len(offers),
        "top_price_drops": drops[:5],
        "cheapest_leaderboard": cheapest_leaderboard,
        "cloud_backup_configured": has_cloud_sync,
        "gist_id": gist_id or ""
    }


# --- API Routes: Backup & Persistence Vault ---
@app.get("/api/backup/export-json")
def export_json_backup(db: Session = Depends(get_db)):
    data = export_full_backup_json(db)
    filename = f"auratech_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/backup/import-json")
async def import_json_backup(
    file: Optional[UploadFile] = File(None),
    mode: str = Form("replace"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    payload = None
    if file:
        content = await file.read()
        payload = json.loads(content.decode("utf-8"))
    else:
        try:
            payload = await request.json()
        except Exception:
            pass

    if not payload:
        raise HTTPException(status_code=400, detail="محتوای فایل پشتیبان ارسال نشده است.")

    res = import_full_backup_json(payload, mode=mode, db=db)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "خطا در بازیابی اطلاعات."))
    return res


@app.get("/api/backup/export-csv")
def export_csv_prices(db: Session = Depends(get_db)):
    csv_str = export_products_csv(db)
    filename = f"auratech_price_list_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        content=csv_str.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/backup/cloud-sync")
async def trigger_cloud_gist_sync(db: Session = Depends(get_db)):
    res = await sync_to_github_gist(db=db)
    return res


@app.post("/api/backup/cloud-restore")
async def trigger_cloud_gist_restore(db: Session = Depends(get_db)):
    res = await restore_from_github_gist(db=db)
    return res


# --- API Routes: Settings ---
@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(AppSetting).all()
    res = {s.key: s.value for s in settings}
    return res


@app.post("/api/settings")
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    fields = {
        "github_backup_token": payload.github_backup_token,
        "github_gist_id": payload.github_gist_id,
        "auto_sync_gist": payload.auto_sync_gist,
        "quote_default_margin": payload.quote_default_margin,
        "quote_default_assembly_fee": payload.quote_default_assembly_fee,
        "quote_default_software_fee": payload.quote_default_software_fee
    }
    for k, v in fields.items():
        if v is not None:
            s = db.query(AppSetting).filter_by(key=k).first()
            if s:
                s.value = v
            else:
                db.add(AppSetting(key=k, value=v))
    db.commit()
    return {"success": True, "message": "تنظیمات با موفقیت ذخیره شدند."}
