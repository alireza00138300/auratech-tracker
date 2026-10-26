import os
os.environ["TESTING"] = "true"
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.seed import seed_database

@pytest.fixture(scope="module")
def client():
    seed_database(force_reseed=True)
    with TestClient(app) as c:
        yield c

def test_get_products_list_and_filtering(client):
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 20
    assert len(data["categories"]) > 0
    assert len(data["brands"]) > 0
    assert len(data["stores"]) > 0

    # Test category filter
    res_cat = client.get("/api/products?category=پردازنده")
    assert res_cat.status_code == 200
    cat_data = res_cat.json()
    assert cat_data["total"] > 0
    for p in cat_data["products"]:
        assert p["category"] == "پردازنده"

    # Test search filter
    res_search = client.get("/api/products?search=13400")
    assert res_search.status_code == 200
    s_data = res_search.json()
    assert s_data["total"] >= 1
    assert "13400" in s_data["products"][0]["name_fa"]

def test_product_crud_and_offers_lifecycle(client):
    # 1. Create a product with initial offer
    new_prod_payload = {
        "name_fa": "کارت گرافیک ام اس آی RTX 4070 Gaming X Slim",
        "name_en": "MSI RTX 4070 Gaming X Slim 12G",
        "category": "کارت گرافیک",
        "brand": "MSI",
        "condition": "نو",
        "image_url": "https://example.com/msi.jpg",
        "initial_offer": {
            "store_name": "اگزو گیم",
            "product_url": "https://exo.ir/product/msi-rtx-4070-slim",
            "current_price": 42500000
        }
    }
    create_res = client.post("/api/products", json=new_prod_payload)
    assert create_res.status_code == 200
    created_prod = create_res.json()
    pid = created_prod["id"]
    assert pid > 0
    assert created_prod["lowest_price"] == 42500000
    assert created_prod["lowest_store_name"] == "اگزو گیم"
    assert len(created_prod["vendor_offers"]) == 1

    # 2. Get Product by ID
    get_res = client.get(f"/api/products/{pid}")
    assert get_res.status_code == 200
    assert get_res.json()["name_fa"] == new_prod_payload["name_fa"]

    # 3. Add second offer with lower price
    add_offer_payload = {
        "store_name": "پیسی ماد",
        "product_url": "https://pcmod.ir/shop/msi-rtx-4070-slim",
        "current_price": 41900000
    }
    offer_res = client.post(f"/api/products/{pid}/offers", json=add_offer_payload)
    assert offer_res.status_code == 200
    updated_prod = offer_res.json()
    assert len(updated_prod["vendor_offers"]) == 2
    # Verify lowest price updated to the cheaper offer
    assert updated_prod["lowest_price"] == 41900000
    assert updated_prod["lowest_store_name"] == "پیسی ماد"

    offer_to_delete = updated_prod["vendor_offers"][1]["id"]

    # 4. Delete one offer
    del_offer_res = client.delete(f"/api/offers/{offer_to_delete}")
    assert del_offer_res.status_code == 200
    
    # Check product offers count decreased
    check_prod = client.get(f"/api/products/{pid}").json()
    assert len(check_prod["vendor_offers"]) == 1

    # 5. Update Product details
    update_res = client.put(f"/api/products/{pid}", json={"name_fa": "کارت گرافیک ام اس آی RTX 4070 (ویرایش شده)"})
    assert update_res.status_code == 200
    assert update_res.json()["name_fa"] == "کارت گرافیک ام اس آی RTX 4070 (ویرایش شده)"

    # 6. Delete Product
    del_prod_res = client.delete(f"/api/products/{pid}")
    assert del_prod_res.status_code == 200
    assert client.get(f"/api/products/{pid}").status_code == 404

def test_scraper_test_url_endpoint(client):
    res = client.post("/api/scraper/test-url", json={"url": "https://exo.ir/product/test-item"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["price"] > 0
    assert "store_name" in data

def test_cron_trigger_and_manual_scrape(client):
    # Test cron trigger endpoint with limit=5
    res_cron = client.get("/api/cron/trigger?limit=5")
    assert res_cron.status_code == 200
    cron_data = res_cron.json()
    assert cron_data["status"] == "ok"
    assert "result" in cron_data
    assert cron_data["result"]["scraped_offers"] == 5

    # Test manual scrape endpoint
    res_manual = client.post("/api/scrape/run?limit=3")
    assert res_manual.status_code == 200
    assert res_manual.json()["scraped_offers"] == 3

def test_market_overview(client):
    res = client.get("/api/market-overview")
    assert res.status_code == 200
    data = res.json()
    assert "tether_toman" in data
    assert data["tether_toman"] > 50000
    assert "cheapest_leaderboard" in data
    assert "total_products" in data
    assert data["total_products"] >= 20

def test_backup_and_export_endpoints(client):
    # JSON Export
    res_json = client.get("/api/backup/export-json")
    assert res_json.status_code == 200
    assert "application/json" in res_json.headers["content-type"]
    backup_data = res_json.json()
    assert "products" in backup_data

    # CSV Export
    res_csv = client.get("/api/backup/export-csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "شناسه" in res_csv.text

    # JSON Import
    res_import = client.post("/api/backup/import-json", json=backup_data)
    assert res_import.status_code == 200
    assert res_import.json()["success"] is True

def test_settings_endpoints(client):
    res = client.get("/api/settings")
    assert res.status_code == 200
    settings = res.json()
    assert "tether_irt_rate" in settings

    # Update settings
    update_res = client.post("/api/settings", json={
        "quote_default_margin": "15",
        "auto_sync_gist": "true"
    })
    assert update_res.status_code == 200
    assert update_res.json()["success"] is True

    # Verify updated
    new_settings = client.get("/api/settings").json()
    assert new_settings["quote_default_margin"] == "15"
    assert new_settings["auto_sync_gist"] == "true"
