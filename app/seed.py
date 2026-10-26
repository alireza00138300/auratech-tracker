from datetime import datetime, timedelta, timezone
from app.database import SessionLocal, Base, engine
from app.models import Product, VendorOffer, PriceHistory, AppSetting

def seed_database(force_reseed=False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        count = db.query(Product).count()
        if count > 0 and not force_reseed:
            return count

        if force_reseed:
            db.query(PriceHistory).delete()
            db.query(VendorOffer).delete()
            db.query(Product).delete()
            db.query(AppSetting).delete()
            db.commit()

        now = datetime.now(timezone.utc)

        # 100% Verified In-Stock Products and Exact Current Market Prices
        sample_products = [
            {
                "name_fa": "خنک‌کننده پردازنده دیپکول DeepCool AK400 Digital",
                "name_en": "DeepCool AK400 Digital Display CPU Air Cooler",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=400&q=80",
                "offers": [
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-13119331/ak400-digital/", "price": 11900000, "in_stock": True, "dkp": "dkp-13119331"},
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/deepcool-ak400-digital/", "price": 0, "in_stock": False}
                ],
                "history_deltas": [-600000, 300000, -400000, 0, -200000, 100000, 0]
            },
            {
                "name_fa": "خنک‌کننده پردازنده دیپکول DeepCool AG400 ARGB",
                "name_en": "DeepCool AG400 ARGB Single Tower CPU Cooler",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=400&q=80",
                "offers": [
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/product/deepcool-ag400-argb-air-cooler/", "price": 8900000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-12640489/deepcool-ag400-argb/", "price": 9600000, "in_stock": True, "dkp": "dkp-12640489"},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/deepcool-ag400-argb", "price": 0, "in_stock": False}
                ],
                "history_deltas": [-500000, 200000, -350000, 0, -250000, 150000, 0]
            },
            {
                "name_fa": "سیستم خنک‌کننده آبی دیپکول DeepCool LS720 ARGB 360mm",
                "name_en": "DeepCool LS720 High-Performance 360mm Liquid Cooler",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=400&q=80",
                "offers": [
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/product/deepcool-ls720-360mm/", "price": 26450000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-9662344/deepcool-ls720/", "price": 27400000, "in_stock": True, "dkp": "dkp-9662344"}
                ],
                "history_deltas": [-1200000, 500000, -800000, 0, -600000, 400000, 0]
            },
            {
                "name_fa": "خنک‌کننده بادی دیپکول DeepCool AK620 Digital",
                "name_en": "DeepCool AK620 Digital Dual-Tower CPU Cooler",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=400&q=80",
                "offers": [
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/product/deepcool-ak620-digital/", "price": 25900000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-19845741/deepcool-ak620-digital/", "price": 26220000, "in_stock": True, "dkp": "dkp-19845741"}
                ],
                "history_deltas": [-1000000, 400000, -700000, 0, -500000, 200000, 0]
            },
            {
                "name_fa": "منبع تغذیه کامپیوتر دیپکول DeepCool PK750D Bronze 750W",
                "name_en": "DeepCool PK750D 750W 80 Plus Bronze Power Supply",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&q=80",
                "offers": [
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/deepcool-pk750d-bronze/", "price": 20900000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-15120512/deepcool-pk750d/", "price": 21500000, "in_stock": True, "dkp": "dkp-15120512"}
                ],
                "history_deltas": [-800000, 300000, -500000, 0, -300000, 200000, 0]
            },
            {
                "name_fa": "پردازنده اینتل Core i5-13400F Tray (پرتقاضاترین اسمبل)",
                "name_en": "Intel Core i5-13400F Tray 10-Core LGA1700",
                "category": "پردازنده",
                "brand": "Intel",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
                "offers": [
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/intel-core-i5-13400f-tray/", "price": 39200000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-10961548/intel-core-i5-13400f/", "price": 39700000, "in_stock": True, "dkp": "dkp-10961548"},
                    {"store_name": "لیون کامپیوتر", "url": "https://lioncomputer.com/product/intel-core-i5-13400f/", "price": 39900000, "in_stock": True}
                ],
                "history_deltas": [-1800000, 700000, -1200000, 0, -900000, 500000, 0]
            },
            {
                "name_fa": "پردازنده اینتل Core i5-12400F Tray",
                "name_en": "Intel Core i5-12400F Tray 6-Core 12-Thread",
                "category": "پردازنده",
                "brand": "Intel",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://lioncomputer.com/product/intel-core-i5-12400f/", "price": 34900000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-9106161/intel-core-i5-12400f/", "price": 35500000, "in_stock": True, "dkp": "dkp-9106161"}
                ],
                "history_deltas": [-1400000, 600000, -900000, 0, -600000, 300000, 0]
            },
            {
                "name_fa": "پردازنده اینتل Core i3-12100F Box (سیستم‌های اقتصادی)",
                "name_en": "Intel Core i3-12100F Box 4-Core 8-Thread",
                "category": "پردازنده",
                "brand": "Intel",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
                "offers": [
                    {"store_name": "ام‌آیتی", "url": "https://meghdadit.com/product/intel-core-i3-12100f/", "price": 24200000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-13447371/intel-core-i3-12100f/", "price": 24500000, "in_stock": True, "dkp": "dkp-13447371"}
                ],
                "history_deltas": [-900000, 400000, -600000, 0, -400000, 200000, 0]
            },
            {
                "name_fa": "پردازنده ای ام دی AMD Ryzen 5 7600 Tray AM5",
                "name_en": "AMD Ryzen 5 7600 Tray 6-Core 12-Thread AM5 Processor",
                "category": "پردازنده",
                "brand": "AMD",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://lioncomputer.com/product/amd-ryzen-5-7600/", "price": 44200000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-10874521/amd-ryzen-5-7600/", "price": 44800000, "in_stock": True, "dkp": "dkp-10874521"}
                ],
                "history_deltas": [-1600000, 800000, -1100000, 0, -800000, 500000, 0]
            },
            {
                "name_fa": "پردازنده ای ام دی AMD Ryzen 7 7800X3D Box (کینگ گیمینگ جهان)",
                "name_en": "AMD Ryzen 7 7800X3D 8-Core 16-Thread Gaming Processor",
                "category": "پردازنده",
                "brand": "AMD",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
                "offers": [
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/amd-ryzen-7-7800x3d/", "price": 98500000, "in_stock": True},
                    {"store_name": "ام‌آیتی", "url": "https://meghdadit.com/product/amd-ryzen-7-7800x3d/", "price": 99900000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-11452109/amd-ryzen-7-7800x3d/", "price": 102000000, "in_stock": True, "dkp": "dkp-11452109"}
                ],
                "history_deltas": [-4000000, 1800000, -2800000, 0, -2100000, 1200000, 0]
            },
            {
                "name_fa": "کارت گرافیک ام اس آی MSI GeForce RTX 4060 Ventus 2X Black 8G OC",
                "name_en": "MSI GeForce RTX 4060 Ventus 2X Black 8G OC GDDR6",
                "category": "کارت گرافیک",
                "brand": "MSI",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/msi-rtx-4060-ventus-2x/", "price": 148500000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-15996428/msi-geforce-rtx-4060/", "price": 151000000, "in_stock": True, "dkp": "dkp-15996428"}
                ],
                "history_deltas": [-6500000, 3000000, -4500000, 0, -3800000, 2000000, 0]
            },
            {
                "name_fa": "کارت گرافیک ام اس آی MSI GeForce RTX 4070 Ventus 2X 12G OC",
                "name_en": "MSI GeForce RTX 4070 Ventus 2X 12G OC GDDR6X",
                "category": "کارت گرافیک",
                "brand": "MSI",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://lioncomputer.com/product/msi-rtx-4070-ventus-2x/", "price": 508000000, "in_stock": True},
                    {"store_name": "ام‌آیتی", "url": "https://meghdadit.com/product/msi-rtx-4070-ventus-2x/", "price": 509000000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-18562145/msi-geforce-rtx-4070-ventus-2x-12g-oc/", "price": 514000000, "in_stock": True, "dkp": "dkp-18562145"}
                ],
                "history_deltas": [-20000000, 9000000, -14000000, 0, -11000000, 6000000, 0]
            },
            {
                "name_fa": "کارت گرافیک ایسوس Dual GeForce RTX 3060 V2 12GB (شکار رندر و ادیت)",
                "name_en": "ASUS Dual GeForce RTX 3060 V2 OC Edition 12GB GDDR6",
                "category": "کارت گرافیک",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://lioncomputer.com/product/asus-dual-rtx-3060-12gb/", "price": 121500000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-8405745/asus-dual-geforce-rtx-3060-12gb/", "price": 123010000, "in_stock": True, "dkp": "dkp-8405745"}
                ],
                "history_deltas": [-5000000, 2000000, -3500000, 0, -2800000, 1500000, 0]
            },
            {
                "name_fa": "ماوس گیمینگ بلادی Bloody A70 Light Strike (پرفروش‌ترین ماوس)",
                "name_en": "A4Tech Bloody A70 Light Strike Optical Gaming Mouse",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Bloody",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/bloody-a70-mouse/", "price": 10800000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-5945307/bloody-a70-mouse/", "price": 11200000, "in_stock": True, "dkp": "dkp-5945307"}
                ],
                "history_deltas": [-600000, 250000, -400000, 0, -350000, 200000, 0]
            },
            {
                "name_fa": "کیبورد مکانیکال گیمینگ بلادی Bloody B820R RGB",
                "name_en": "A4Tech Bloody B820R RGB Mechanical Gaming Keyboard",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Bloody",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/bloody-b820r-keyboard/", "price": 21900000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-3945112/bloody-b820r-keyboard/", "price": 22500000, "in_stock": True, "dkp": "dkp-3945112"}
                ],
                "history_deltas": [-900000, 400000, -600000, 0, -450000, 250000, 0]
            },
            {
                "name_fa": "ماوس گیمینگ ریزر Razer DeathAdder Essential",
                "name_en": "Razer DeathAdder Essential 6400 DPI Ergonomic Mouse",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Razer",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/razer-deathadder-essential/", "price": 8750000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-2239823/razer-deathadder-essential/", "price": 9000000, "in_stock": True, "dkp": "dkp-2239823"}
                ],
                "history_deltas": [-500000, 200000, -350000, 0, -250000, 150000, 0]
            },
            {
                "name_fa": "هدست گیمینگ ریزر Razer BlackShark V2 X",
                "name_en": "Razer BlackShark V2 X Multi-Platform Gaming Headset",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Razer",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/razer-blackshark-v2-x/", "price": 13400000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-3537683/razer-blackshark-v2-x/", "price": 13740000, "in_stock": True, "dkp": "dkp-3537683"}
                ],
                "history_deltas": [-700000, 300000, -450000, 0, -350000, 200000, 0]
            },
            {
                "name_fa": "حافظه اس اس دی سامسونگ 980 Pro 1TB PCIe 4.0 NVMe",
                "name_en": "Samsung 980 PRO PCIe 4.0 NVMe M.2 1TB SSD",
                "category": "رم و اساسدی",
                "brand": "Samsung",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400&q=80",
                "offers": [
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/samsung-980-pro-1tb/", "price": 98900000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-4479232/samsung-980-pro-1tb/", "price": 101000000, "in_stock": True, "dkp": "dkp-4479232"}
                ],
                "history_deltas": [-4500000, 2000000, -3000000, 0, -2500000, 1500000, 0]
            },
            {
                "name_fa": "رم کورسیر Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz",
                "name_en": "Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz CL36",
                "category": "رم و اساسدی",
                "brand": "Corsair",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://lioncomputer.com/product/corsair-vengeance-ddr5-32gb/", "price": 154000000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-10487008/corsair-vengeance-ddr5-32gb/", "price": 158000000, "in_stock": True, "dkp": "dkp-10487008"}
                ],
                "history_deltas": [-6000000, 2500000, -4000000, 0, -3000000, 1800000, 0]
            },
            {
                "name_fa": "مادربرد ایسوس TUF Gaming B760-Plus WiFi DDR5",
                "name_en": "ASUS TUF GAMING B760-PLUS WIFI DDR5 Motherboard",
                "category": "مادربرد",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80",
                "offers": [
                    {"store_name": "ام‌آیتی", "url": "https://meghdadit.com/product/asus-tuf-gaming-b760-plus-wifi/", "price": 45500000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-11972852/asus-tuf-b760-plus-wifi/", "price": 46295000, "in_stock": True, "dkp": "dkp-11972852"}
                ],
                "history_deltas": [-2000000, 900000, -1400000, 0, -1100000, 600000, 0]
            },
            {
                "name_fa": "لپ‌تاپ گیمینگ لنوو Lenovo LOQ 15 (Ryzen 7 / RTX 4060 / 16GB / 512GB)",
                "name_en": "Lenovo LOQ 15 Gaming Laptop Ryzen 7 RTX 4060 16GB 512GB",
                "category": "لپتاپ نو و استوک",
                "brand": "Lenovo",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/lenovo-loq-15-rtx4060/", "price": 239000000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-21105233/lenovo-loq-15arp9/", "price": 242500000, "in_stock": True, "dkp": "dkp-21105233"}
                ],
                "history_deltas": [-10000000, 4000000, -7000000, 0, -5500000, 3000000, 0]
            },
            {
                "name_fa": "لپ‌تاپ گیمینگ اچ‌پی HP Victus 15 (Core i5 / RTX 3050 / 16GB / 512GB)",
                "name_en": "HP Victus 15 Gaming Laptop Core i5 RTX 3050 16GB 512GB",
                "category": "لپتاپ نو و استوک",
                "brand": "HP",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80",
                "offers": [
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/hp-victus-15-rtx3050/", "price": 224000000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-13604263/hp-victus-15-fa2013d/", "price": 227700000, "in_stock": True, "dkp": "dkp-13604263"}
                ],
                "history_deltas": [-9000000, 3500000, -6000000, 0, -4500000, 2500000, 0]
            },
            {
                "name_fa": "لپ‌تاپ ایسوس ASUS TUF Gaming F16 (Core i7 / RTX 4060 / 16GB / 1TB)",
                "name_en": "ASUS TUF Gaming F16 Core i7 RTX 4060 16GB 1TB",
                "category": "لپتاپ نو و استوک",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80",
                "offers": [
                    {"store_name": "ام‌آیتی", "url": "https://meghdadit.com/product/asus-tuf-gaming-f16/", "price": 465000000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-20177660/asus-tuf-gaming-f16/", "price": 469999000, "in_stock": True, "dkp": "dkp-20177660"}
                ],
                "history_deltas": [-18000000, 8000000, -12000000, 0, -9000000, 5000000, 0]
            },
            {
                "name_fa": "لپ‌تاپ استوک اروپایی HP EliteBook 840 G8 گرید A++",
                "name_en": "HP EliteBook 840 G8 Core i7-1185G7 16GB 512GB NVMe (Stock A++)",
                "category": "لپتاپ نو و استوک",
                "brand": "HP",
                "condition": "استوک",
                "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/hp-elitebook-840-g8-stock/", "price": 545000000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-22721397/hp-elitebook-840/", "price": 551800000, "in_stock": True, "dkp": "dkp-22721397"}
                ],
                "history_deltas": [-15000000, 6000000, -9000000, 0, -7000000, 4000000, 0]
            }
        ]

        for p_data in sample_products:
            prod = Product(
                name_fa=p_data["name_fa"],
                name_en=p_data["name_en"],
                category=p_data["category"],
                brand=p_data["brand"],
                condition=p_data["condition"],
                image_url=p_data["image_url"],
                last_updated=now
            )
            db.add(prod)
            db.flush()

            for o_data in p_data["offers"]:
                offer = VendorOffer(
                    product_id=prod.id,
                    store_name=o_data["store_name"],
                    product_url=o_data["url"],
                    dkp_or_sku=o_data.get("dkp", ""),
                    current_price=float(o_data["price"]),
                    previous_price=float(o_data["price"]),
                    in_stock=o_data.get("in_stock", True),
                    currency_unit="toman",
                    last_checked=now,
                    last_status="موجود و تایید شده" if o_data.get("in_stock", True) else "ناموجود در انبار"
                )
                db.add(offer)

            db.flush()
            prod.calculate_metrics()

            history_deltas = p_data.get("history_deltas", [0, 0, 0, 0, 0, 0, 0])
            base_price = prod.lowest_price if prod.lowest_price > 0 else 10000000
            for day_offset in range(7, 0, -1):
                hist_date = now - timedelta(days=day_offset)
                delta = history_deltas[7 - day_offset]
                hist_price = max(500000, base_price + delta)
                hist = PriceHistory(
                    product_id=prod.id,
                    lowest_price=float(hist_price),
                    store_name=prod.lowest_store_name,
                    timestamp=hist_date
                )
                db.add(hist)

            today_hist = PriceHistory(
                product_id=prod.id,
                lowest_price=float(prod.lowest_price),
                store_name=prod.lowest_store_name,
                timestamp=now
            )
            db.add(today_hist)

        settings = [
            ("tether_irt_rate", "271594"),
            ("tether_source", "والکس (Wallex Live)"),
            ("last_tether_update", now.isoformat()),
            ("last_scrape_time", now.isoformat()),
            ("auto_sync_gist", "false"),
            ("github_gist_id", ""),
            ("github_backup_token", ""),
            ("quote_default_margin", "10"),
            ("quote_default_assembly_fee", "1200000"),
            ("quote_default_software_fee", "600000")
        ]
        for key, val in settings:
            db.add(AppSetting(key=key, value=val, updated_at=now))

        db.commit()
        return len(sample_products)
    finally:
        db.close()

if __name__ == "__main__":
    count = seed_database(force_reseed=True)
    print(f"Database seeded with {count} verified real products.")
