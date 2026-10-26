import pytest
import asyncio
from app.scraper import (
    parse_price_string,
    detect_store_name,
    extract_digikala_id,
    MultiLayerScraper,
    fetch_nobitex_tether
)

def test_price_string_normalization_and_rial_conversion():
    # Persian digits with Toman
    p1 = parse_price_string("۱۲,۵۰۰,۰۰۰ تومان")
    assert p1 == 12500000.0

    # Rial conversion (divide by 10)
    p2 = parse_price_string("۱۲۵,۰۰۰,۰۰۰ ریال")
    assert p2 == 12500000.0

    # English string with commas
    p3 = parse_price_string("11,490,000")
    assert p3 == 11490000.0

    # Force unit rial
    p4 = parse_price_string("50000000", force_unit="rial")
    assert p4 == 5000000.0

    # Empty string
    assert parse_price_string("") == 0.0

def test_store_domain_detection():
    assert detect_store_name("https://exo.ir/product/test") == "اگزو گیم"
    assert detect_store_name("https://pcmod.ir/shop/test") == "پیسی ماد"
    assert detect_store_name("https://karmait.shop/item/1") == "کارما آیتی"
    assert detect_store_name("https://toprayan.com/product/123") == "تاپ رایان"
    assert detect_store_name("https://tcg.ir/product/bloody") == "تخت جمشید"
    assert detect_store_name("https://digikala.com/product/dkp-100") == "دیجیکالا"

def test_extract_digikala_id():
    assert extract_digikala_id("https://www.digikala.com/product/dkp-10543210/cpu") == "10543210"
    assert extract_digikala_id("dkp-998877") == "998877"
    assert extract_digikala_id("1234567") == "1234567"

def test_layer2_torob_emalls_meta_tags():
    scraper = MultiLayerScraper()
    html_torob = """
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <title>پردازنده اینتل Core i5 13400F | اگزو گیم</title>
        <meta property="og:title" content="پردازنده اینتل Core i5 13400F">
        <meta property="product:price:amount" content="11450000">
        <meta property="product:price:currency" content="IRT">
        <meta property="product:availability" content="instock">
    </head>
    <body><h1>پردازنده اینتل Core i5 13400F</h1></body>
    </html>
    """
    res = scraper.extract_layer2_meta_tags(html_torob, "https://exo.ir/product/i5-13400f")
    assert res is not None
    assert res["price"] == 11450000.0
    assert res["in_stock"] is True
    assert "Torob/Emalls" in res["layer"]

    # Test out of stock meta
    html_out = """
    <html><head>
    <meta name="torob:price" content="24,500,000">
    <meta name="availability" content="outofstock">
    </head></html>
    """
    res_out = scraper.extract_layer2_meta_tags(html_out, "https://toprayan.com/item")
    assert res_out is not None
    assert res_out["price"] == 24500000.0
    assert res_out["in_stock"] is False

def test_layer3_schema_org_jsonld():
    scraper = MultiLayerScraper()
    html_jsonld = """
    <!DOCTYPE html>
    <html>
    <head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": "خنک‌کننده دیپکول LS720",
            "image": "https://pcmod.ir/img/ls720.jpg",
            "offers": {
                "@type": "Offer",
                "priceCurrency": "IRT",
                "price": "7650000",
                "availability": "https://schema.org/InStock"
            }
        }
        </script>
    </head>
    </html>
    """
    res = scraper.extract_layer3_jsonld(html_jsonld, "https://pcmod.ir/shop/ls720")
    assert res is not None
    assert res["title"] == "خنک‌کننده دیپکول LS720"
    assert res["price"] == 7650000.0
    assert res["in_stock"] is True
    assert "JSON-LD" in res["layer"]

def test_layer4_css_selectors():
    scraper = MultiLayerScraper()
    html_css = """
    <html>
    <body>
        <h1>ماوس گیمینگ بلادی A70</h1>
        <div class="summary">
            <span class="price"><ins><span class="amount">۱,۳۹۰,۰۰۰ تومان</span></ins></span>
        </div>
    </body>
    </html>
    """
    res = scraper.extract_layer4_selectors(html_css, "https://exo.ir/product/bloody-a70")
    assert res is not None
    assert res["price"] == 1390000.0
    assert res["title"] == "ماوس گیمینگ بلادی A70"

@pytest.mark.anyio
async def test_full_scraper_simulation_fallback():
    scraper = MultiLayerScraper()
    res = await scraper.scrape_url("https://exo.ir/product/intel-core-i5-13400f")
    assert res["success"] is True
    assert res["price"] > 0
    assert res["store_name"] == "اگزو گیم"

@pytest.mark.anyio
async def test_nobitex_tether_fetch():
    result = await fetch_nobitex_tether()
    assert "tether_toman" in result
    assert result["tether_toman"] > 50000
