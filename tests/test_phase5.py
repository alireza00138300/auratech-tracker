import os
os.environ["TESTING"] = "true"
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_template_rendering_and_rtl_persian(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    assert 'dir="rtl"' in html
    assert 'lang="fa"' in html
    assert "AuraTech Tracker" in html
    assert "سامانه پایش هوشمند بازار سخت‌افزار" in html
    assert "manifest.json" in html
    assert "static/css/style.css" in html
    assert "static/js/app.js" in html

def test_pwa_manifest_validity(client):
    res = client.get("/static/manifest.json")
    assert res.status_code == 200
    manifest = res.json()
    assert manifest["display"] == "standalone"
    assert manifest["theme_color"] == "#08080A"
    assert manifest["background_color"] == "#08080A"
    assert len(manifest["icons"]) >= 2

def test_service_worker_asset(client):
    res = client.get("/static/sw.js")
    assert res.status_code == 200
    assert "CACHE_NAME" in res.text
    assert "addEventListener('fetch'" in res.text

def test_css_design_system_integrity(client):
    res = client.get("/static/css/style.css")
    assert res.status_code == 200
    css = res.text
    assert "#08080A" in css
    assert "#D4AF37" in css
    assert "Vazirmatn" in css
    assert ".gold-gradient-text" in css
    assert ".bottom-nav" in css

def test_js_app_integrity(client):
    res = client.get("/static/js/app.js")
    assert res.status_code == 200
    js = res.text
    assert "fetchProducts" in js
    assert "addToQuote" in js
    assert "copyQuoteForCustomer" in js
    assert "testScraperUrl" in js
    assert "uploadRestoreBackup" in js
    assert "triggerGistSyncNow" in js

def test_pwa_icons_availability(client):
    res192 = client.get("/static/icons/icon-192.png")
    assert res192.status_code == 200
    assert res192.headers["content-type"] == "image/png"

    res512 = client.get("/static/icons/icon-512.png")
    assert res512.status_code == 200
    assert res512.headers["content-type"] == "image/png"
