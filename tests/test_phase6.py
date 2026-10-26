import os
import pytest

def test_deployment_files_exist():
    assert os.path.exists("requirements.txt")
    assert os.path.exists("render.yaml")
    assert os.path.exists("Procfile")
    assert os.path.exists(".env.example")
    assert os.path.exists("README.md")

def test_requirements_content():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        content = f.read()
    assert "fastapi" in content
    assert "uvicorn" in content
    assert "sqlalchemy" in content
    assert "httpx" in content
    assert "apscheduler" in content
    assert "beautifulsoup4" in content

def test_render_yaml_configuration():
    with open("render.yaml", "r", encoding="utf-8") as f:
        content = f.read()
    assert "auratech-tracker" in content
    assert "--workers 1" in content
    assert "--limit-concurrency 30" in content
    assert "pip install -r requirements.txt" in content

def test_procfile_configuration():
    with open("Procfile", "r", encoding="utf-8") as f:
        content = f.read()
    assert "web: uvicorn app.main:app" in content
    assert "--workers 1" in content

def test_readme_persian_documentation():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "AuraTech Tracker" in content
    assert "دیجیکالا" in content
    assert "اگزو گیم" in content
    assert "پیسی ماد" in content
    assert "Render.com" in content
    assert "cron-job.org" in content
    assert "GitHub Gist" in content
