from datetime import datetime, timedelta, timezone
from app.database import SessionLocal, Base, engine
from app.models import Product, VendorOffer, PriceHistory, AppSetting

def seed_database(force_reseed=False):
    # Ensure tables exist
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

        sample_products = [
            {
                "name_fa": "پردازنده اینتل Core i5-13400F Tray",
                "name_en": "Intel Core i5-13400F Tray 10-Core LGA1700",
                "category": "پردازنده",
                "brand": "Intel",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/intel-core-i5-13400f-tray", "price": 11450000, "in_stock": True},
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/intel-core-i5-13400f", "price": 11590000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-10543210/cpu-intel-13400f", "price": 11800000, "in_stock": True, "dkp": "dkp-10543210"},
                    {"store_name": "ام‌آیتی", "url": "https://mitgroup.ir/intel-i5-13400f-tray", "price": 11490000, "in_stock": True}
                ],
                "history_deltas": [-300000, -200000, 100000, -150000, 50000, -250000, 0]
            },
            {
                "name_fa": "پردازنده اینتل Core i3-12100F Tray",
                "name_en": "Intel Core i3-12100F Tray 4-Core 8-Thread",
                "category": "پردازنده",
                "brand": "Intel",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80",
                "offers": [
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/intel-core-i3-12100f", "price": 4650000, "in_stock": True},
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/intel-core-i3-12100f-tray", "price": 4720000, "in_stock": True},
                    {"store_name": "آریا کامپیوتر", "url": "https://ariacomputer.ir/intel-i3-12100f-tray", "price": 4690000, "in_stock": True}
                ],
                "history_deltas": [-50000, 100000, -70000, 0, 50000, -90000, 0]
            },
            {
                "name_fa": "پردازنده ای ام دی Ryzen 5 7600X",
                "name_en": "AMD Ryzen 5 7600X 6-Core 4.7GHz AM5",
                "category": "پردازنده",
                "brand": "AMD",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1555617981-d3a542b6a9e1?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/amd-ryzen-5-7600x-cpu", "price": 14200000, "in_stock": True},
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/amd-ryzen-5-7600x", "price": 14450000, "in_stock": True},
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/amd-ryzen-5-7600x", "price": 14100000, "in_stock": True}
                ],
                "history_deltas": [-400000, -200000, 300000, -100000, -250000, 150000, 0]
            },
            {
                "name_fa": "کارت گرافیک ایسوس ROG Strix RTX 4060 OC 8GB",
                "name_en": "ASUS ROG Strix GeForce RTX 4060 OC Edition 8GB GDDR6",
                "category": "کارت گرافیک",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/asus-rog-strix-rtx-4060-oc-8gb", "price": 28900000, "in_stock": True},
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/asus-rog-strix-rtx4060-oc-8g", "price": 29400000, "in_stock": True},
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/asus-rog-strix-rtx4060", "price": 28650000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-1289456/asus-rog-rtx-4060", "price": 29800000, "in_stock": True, "dkp": "dkp-1289456"}
                ],
                "history_deltas": [-800000, -500000, 200000, -400000, 600000, -350000, 0]
            },
            {
                "name_fa": "کارت گرافیک ام اس آی GeForce RTX 4060 Ti Gaming X 8GB",
                "name_en": "MSI GeForce RTX 4060 Ti Gaming X 8G Twin Frozr 9",
                "category": "کارت گرافیک",
                "brand": "MSI",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/msi-rtx-4060-ti-gaming-x-8g", "price": 31500000, "in_stock": True},
                    {"store_name": "ام‌آیتی", "url": "https://mitgroup.ir/msi-rtx-4060-ti-gaming-x-8g", "price": 31200000, "in_stock": True},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/msi-rtx-4060-ti-gaming-x-8g", "price": 31800000, "in_stock": True}
                ],
                "history_deltas": [-500000, 300000, -400000, 200000, -600000, 100000, 0]
            },
            {
                "name_fa": "خنک‌کننده پردازنده دیپکول DeepCool AK400 Digital",
                "name_en": "DeepCool AK400 Digital Display CPU Air Cooler",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=400&q=80",
                "offers": [
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/deepcool-ak400-digital", "price": 2850000, "in_stock": True},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/deepcool-ak400-digital-cpu-cooler", "price": 2790000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-11223344/deepcool-ak400-digital", "price": 2980000, "in_stock": True, "dkp": "dkp-11223344"}
                ],
                "history_deltas": [-120000, 50000, -80000, 0, -60000, 100000, 0]
            },
            {
                "name_fa": "خنک‌کننده مایع دیپکول DeepCool LS720 ARGB 360mm",
                "name_en": "DeepCool LS720 High-Performance 360mm Liquid Cooler",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=400&q=80",
                "offers": [
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/deepcool-ls720-360mm", "price": 7650000, "in_stock": True},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/deepcool-ls720-argb-liquid-cooler", "price": 7490000, "in_stock": True},
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/deepcool-ls720-argb", "price": 7800000, "in_stock": True}
                ],
                "history_deltas": [-300000, 150000, -250000, 0, 100000, -310000, 0]
            },
            {
                "name_fa": "خنک‌کننده بادی دیپکول DeepCool AG400 ARGB",
                "name_en": "DeepCool AG400 ARGB Single Tower CPU Cooler",
                "category": "کولینگ و دیپکول",
                "brand": "DeepCool",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=400&q=80",
                "offers": [
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/deepcool-ag400-argb", "price": 1780000, "in_stock": True},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/deepcool-ag400-argb", "price": 1720000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-1155667/deepcool-ag400", "price": 1850000, "in_stock": True, "dkp": "dkp-1155667"}
                ],
                "history_deltas": [-80000, 40000, -50000, 20000, -60000, 0, 0]
            },
            {
                "name_fa": "ماوس گیمینگ بلادی Bloody A70 Light Strike",
                "name_en": "A4Tech Bloody A70 Light Strike Gaming Mouse",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Bloody",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400&q=80",
                "offers": [
                    {"store_name": "تخت جمشید", "url": "https://tcg.ir/product/bloody-a70-gaming-mouse", "price": 1390000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-458921/bloody-a70", "price": 1480000, "in_stock": True, "dkp": "dkp-458921"},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/bloody-a70-optical-mouse", "price": 1420000, "in_stock": True}
                ],
                "history_deltas": [-100000, 50000, -60000, 0, 40000, -30000, 0]
            },
            {
                "name_fa": "کیبورد مکانیکال بلادی Bloody B820R Light Strike RGB",
                "name_en": "Bloody B820R Light Strike Optical Mechanical Gaming Keyboard",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Bloody",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&q=80",
                "offers": [
                    {"store_name": "تخت جمشید", "url": "https://tcg.ir/product/bloody-b820r-keyboard", "price": 3450000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-789654/bloody-b820r", "price": 3650000, "in_stock": True, "dkp": "dkp-789654"},
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/bloody-b820r-rgb", "price": 3520000, "in_stock": True}
                ],
                "history_deltas": [-150000, 80000, -100000, 0, -80000, 50000, 0]
            },
            {
                "name_fa": "ماوس گیمینگ ریزر Razer DeathAdder Essential",
                "name_en": "Razer DeathAdder Essential 6400 DPI Ergonomic Mouse",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Razer",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/razer-deathadder-essential", "price": 1490000, "in_stock": True},
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/razer-deathadder-essential", "price": 1450000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-234567/razer-deathadder-essential", "price": 1560000, "in_stock": True, "dkp": "dkp-234567"}
                ],
                "history_deltas": [-90000, 40000, -50000, 0, -40000, 30000, 0]
            },
            {
                "name_fa": "هدست گیمینگ ریزر Razer BlackShark V2 X",
                "name_en": "Razer BlackShark V2 X Multi-Platform Gaming Headset",
                "category": "موس و کیبورد گیمینگ",
                "brand": "Razer",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/razer-blackshark-v2-x", "price": 2890000, "in_stock": True},
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/razer-blackshark-v2-x", "price": 2950000, "in_stock": True},
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/razer-blackshark-v2-x", "price": 2820000, "in_stock": True}
                ],
                "history_deltas": [-180000, 70000, -120000, 0, 50000, -70000, 0]
            },
            {
                "name_fa": "ماوس گیمینگ ایسوس ROG Gladius III Wireless AimPoint",
                "name_en": "ASUS ROG Gladius III Wireless AimPoint 36K DPI",
                "category": "موس و کیبورد گیمینگ",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400&q=80",
                "offers": [
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/asus-rog-gladius-iii-wireless-aimpoint", "price": 6190000, "in_stock": True},
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/asus-rog-gladius-iii-aimpoint", "price": 6350000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-876543/rog-gladius-iii", "price": 6490000, "in_stock": True, "dkp": "dkp-876543"}
                ],
                "history_deltas": [-250000, 100000, -150000, 0, -200000, 100000, 0]
            },
            {
                "name_fa": "حافظه اس اس دی سامسونگ Samsung 980 Pro 1TB NVMe",
                "name_en": "Samsung 980 PRO PCIe 4.0 NVMe M.2 1TB SSD",
                "category": "رم و اساسدی",
                "brand": "Samsung",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/samsung-980-pro-1tb", "price": 5350000, "in_stock": True},
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/samsung-980-pro-1tb-nvme", "price": 5290000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-3456789/samsung-980-pro-1tb", "price": 5480000, "in_stock": True, "dkp": "dkp-3456789"},
                    {"store_name": "ام‌آیتی", "url": "https://mitgroup.ir/samsung-980-pro-1tb", "price": 5250000, "in_stock": True}
                ],
                "history_deltas": [-220000, 110000, -90000, 0, -150000, 60000, 0]
            },
            {
                "name_fa": "رم کورسیر Corsair Vengeance RGB 32GB DDR5 6000MHz",
                "name_en": "Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz CL36",
                "category": "رم و اساسدی",
                "brand": "Corsair",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/corsair-vengeance-rgb-32gb-ddr5-6000", "price": 7950000, "in_stock": True},
                    {"store_name": "پیسی ماد", "url": "https://pcmod.ir/shop/corsair-vengeance-rgb-32gb-6000mhz", "price": 8100000, "in_stock": True},
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/corsair-vengeance-ddr5-32gb", "price": 7880000, "in_stock": True}
                ],
                "history_deltas": [-310000, 120000, -180000, 0, -120000, 90000, 0]
            },
            {
                "name_fa": "مادربرد ایسوس TUF Gaming B760-Plus WiFi DDR5",
                "name_en": "ASUS TUF GAMING B760-PLUS WIFI DDR5 Motherboard",
                "category": "مادربرد",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80",
                "offers": [
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/asus-tuf-gaming-b760-plus-wifi", "price": 12850000, "in_stock": True},
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/asus-tuf-b760-plus-wifi-ddr5", "price": 12690000, "in_stock": True},
                    {"store_name": "ام‌آیتی", "url": "https://mitgroup.ir/asus-tuf-b760-plus-wifi", "price": 12750000, "in_stock": True}
                ],
                "history_deltas": [-450000, 200000, -300000, 0, -220000, 150000, 0]
            },
            {
                "name_fa": "لپ‌تاپ لنوو LOQ 15IRX9 (i7-13650HX / 16GB / 512GB / RTX 4060)",
                "name_en": "Lenovo LOQ 15IRX9 Core i7-13650HX 16GB 512GB SSD RTX 4060",
                "category": "لپتاپ نو و استوک",
                "brand": "Lenovo",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/lenovo-loq-15irx9-rtx4060", "price": 63900000, "in_stock": True},
                    {"store_name": "ام‌آیتی", "url": "https://mitgroup.ir/lenovo-loq-15irx9-i7-4060", "price": 64500000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-99887766/lenovo-loq-15irx9", "price": 65900000, "in_stock": True, "dkp": "dkp-99887766"},
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/lenovo-loq-15-rtx4060", "price": 64200000, "in_stock": True}
                ],
                "history_deltas": [-1500000, 800000, -1000000, 0, -1200000, 600000, 0]
            },
            {
                "name_fa": "لپ‌تاپ ایسوس TUF Gaming F15 (i7-12700H / 16GB / 512GB / RTX 4050)",
                "name_en": "ASUS TUF Gaming F15 FX507VU Core i7 16GB 512GB RTX 4050",
                "category": "لپتاپ نو و استوک",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/asus-tuf-f15-rtx4050", "price": 57800000, "in_stock": True},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/asus-tuf-gaming-f15-fx507vu", "price": 58400000, "in_stock": True},
                    {"store_name": "دیجیکالا", "url": "https://www.digikala.com/product/dkp-44332211/asus-tuf-f15", "price": 59500000, "in_stock": True, "dkp": "dkp-44332211"}
                ],
                "history_deltas": [-1200000, 600000, -800000, 0, 900000, -1100000, 0]
            },
            {
                "name_fa": "لپ‌تاپ ایسوس ROG Strix G16 (i9-14900HX / 32GB / 1TB / RTX 4070)",
                "name_en": "ASUS ROG Strix G16 G614JIR Core i9-14900HX 32GB 1TB RTX 4070",
                "category": "لپتاپ نو و استوک",
                "brand": "ASUS ROG",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/asus-rog-strix-g16-rtx4070", "price": 118500000, "in_stock": True},
                    {"store_name": "اگزو گیم", "url": "https://exo.ir/product/asus-rog-strix-g16-g614jir", "price": 119900000, "in_stock": True},
                    {"store_name": "ام‌آیتی", "url": "https://mitgroup.ir/asus-rog-strix-g16-i9-4070", "price": 121000000, "in_stock": True}
                ],
                "history_deltas": [-2500000, 1500000, -2000000, 0, -1800000, 1200000, 0]
            },
            {
                "name_fa": "لپ‌تاپ ام اس آی Cyborg 15 (i7-12650H / 16GB / 512GB / RTX 4060)",
                "name_en": "MSI Cyborg 15 A12VF Core i7 16GB 512GB RTX 4060",
                "category": "لپتاپ نو و استوک",
                "brand": "MSI",
                "condition": "نو",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/msi-cyborg-15-rtx4060", "price": 54900000, "in_stock": True},
                    {"store_name": "ام‌آیتی", "url": "https://mitgroup.ir/msi-cyborg-15-a12vf", "price": 55500000, "in_stock": True},
                    {"store_name": "لیون کامپیوتر", "url": "https://www.lioncomputer.com/product/msi-cyborg-15-rtx4060", "price": 55900000, "in_stock": True}
                ],
                "history_deltas": [-1100000, 500000, -700000, 0, -900000, 400000, 0]
            },
            {
                "name_fa": "لپ‌تاپ استوک اروپایی HP EliteBook 840 G8 گرید A++",
                "name_en": "HP EliteBook 840 G8 Core i7-1185G7 16GB 512GB NVMe (Stock)",
                "category": "لپتاپ نو و استوک",
                "brand": "HP",
                "condition": "استوک",
                "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400&q=80",
                "offers": [
                    {"store_name": "کارما آیتی", "url": "https://karmait.shop/product/hp-elitebook-840-g8-stock", "price": 24800000, "in_stock": True},
                    {"store_name": "تاپ رایان", "url": "https://toprayan.com/product/hp-elitebook-840-g8-refurbished", "price": 25400000, "in_stock": True},
                    {"store_name": "آریا کامپیوتر", "url": "https://ariacomputer.ir/hp-elitebook-840-g8-stock", "price": 24900000, "in_stock": True}
                ],
                "history_deltas": [-600000, 300000, -400000, 0, -500000, 200000, 0]
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

            # Add vendor offers
            for o_data in p_data["offers"]:
                offer = VendorOffer(
                    product_id=prod.id,
                    store_name=o_data["store_name"],
                    product_url=o_data["url"],
                    dkp_or_sku=o_data.get("dkp", ""),
                    current_price=float(o_data["price"]),
                    previous_price=float(o_data["price"] + 200000),
                    in_stock=o_data.get("in_stock", True),
                    currency_unit="toman",
                    last_checked=now,
                    last_status="موجود (پایش موفق)"
                )
                db.add(offer)

            db.flush()
            prod.calculate_metrics()

            # Generate 7-day price history
            history_deltas = p_data.get("history_deltas", [0, 0, 0, 0, 0, 0, 0])
            base_price = prod.lowest_price
            for day_offset in range(7, 0, -1):
                hist_date = now - timedelta(days=day_offset)
                delta = history_deltas[7 - day_offset]
                hist_price = max(100000, base_price + delta)
                hist = PriceHistory(
                    product_id=prod.id,
                    lowest_price=float(hist_price),
                    store_name=prod.lowest_store_name,
                    timestamp=hist_date
                )
                db.add(hist)

            # Today's price point in history
            today_hist = PriceHistory(
                product_id=prod.id,
                lowest_price=float(prod.lowest_price),
                store_name=prod.lowest_store_name,
                timestamp=now
            )
            db.add(today_hist)

        # Default settings
        settings = [
            ("tether_irt_rate", "98500"),
            ("last_tether_update", now.isoformat()),
            ("last_scrape_time", now.isoformat()),
            ("auto_sync_gist", "false"),
            ("github_gist_id", ""),
            ("github_backup_token", ""),
            ("quote_default_margin", "12"),
            ("quote_default_assembly_fee", "450000"),
            ("quote_default_software_fee", "250000")
        ]
        for key, val in settings:
            db.add(AppSetting(key=key, value=val, updated_at=now))

        db.commit()
        return len(sample_products)
    finally:
        db.close()

if __name__ == "__main__":
    count = seed_database(force_reseed=True)
    print(f"Successfully seeded database with {count} Iranian hardware products!")
