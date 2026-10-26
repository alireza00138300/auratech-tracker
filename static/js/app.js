// AuraTech Tracker - Luxury Black & Gold Frontend Logic

// --- PWA Service Worker Registration ---
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => console.log('AuraTech PWA Service Worker registered:', reg.scope))
      .catch(err => console.log('Service Worker registration failed:', err));
  });
}

// --- State Management ---
const state = {
  currentTab: 'market',
  products: [],
  filteredProducts: [],
  categories: [],
  brands: [],
  stores: [],
  overview: {},
  activeCategory: 'همه',
  activeBrand: 'همه',
  activeStore: 'همه',
  activeCondition: 'همه',
  activeSort: 'lowest_price_asc',
  searchQuery: '',
  huntingOnly: false,
  quoteItems: [],
  quoteMarginPercent: 12,
  quoteColleagueDiscount: 0,
  quoteAssemblyFee: 450000,
  quoteSoftwareFee: 250000,
  isScraping: false
};

// --- Persian Utilities ---
function formatPrice(num) {
  if (num === null || num === undefined || isNaN(num)) return '۰';
  return Math.round(num).toLocaleString('fa-IR');
}

function toPersianDigits(str) {
  if (str === null || str === undefined) return '';
  const p = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  return str.toString().replace(/[0-9]/g, d => p[+d]);
}

function showToast(message, type = 'gold') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <span style="color: ${type === 'emerald' ? '#10B981' : type === 'ruby' ? '#EF4444' : '#D4AF37'}; font-size: 1.1rem;">✦</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// --- Tab Switching ---
function switchTab(tabId) {
  state.currentTab = tabId;
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

  const targetPane = document.getElementById(`tab-${tabId}`);
  const targetNav = document.getElementById(`nav-${tabId}`);
  if (targetPane) targetPane.classList.add('active');
  if (targetNav) targetNav.classList.add('active');

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// --- API Calls ---
async function fetchOverview() {
  try {
    const res = await fetch('/api/market-overview');
    if (res.ok) {
      state.overview = await res.json();
      renderOverview();
    }
  } catch (err) {
    console.error('Failed to fetch market overview:', err);
  }
}

async function fetchProducts() {
  try {
    const params = new URLSearchParams();
    if (state.activeCategory !== 'همه' && state.activeCategory !== '🎯 شکار فرصت‌های آربیتراژ') {
      params.append('category', state.activeCategory);
    }
    if (state.huntingOnly) params.append('hunting_only', 'true');
    if (state.activeBrand !== 'همه') params.append('brand', state.activeBrand);
    if (state.activeStore !== 'همه') params.append('store', state.activeStore);
    if (state.activeCondition !== 'همه') params.append('condition', state.activeCondition);
    if (state.activeSort) params.append('sort_by', state.activeSort);
    if (state.searchQuery) params.append('search', state.searchQuery);

    const res = await fetch(`/api/products?${params.toString()}`);
    if (res.ok) {
      const data = await res.json();
      state.products = data.products || [];
      state.categories = data.categories || [];
      state.brands = data.brands || [];
      state.stores = data.stores || [];
      renderCategoryPills();
      renderDropdownFilters();
      renderProductsGrid();
      renderManageProductsList();
    }
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

async function triggerScrape() {
  if (state.isScraping) return;
  state.isScraping = true;
  const syncBtn = document.getElementById('btn-sync-all');
  if (syncBtn) {
    syncBtn.innerHTML = `
      <svg class="spin-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
      در حال پایش بازار...
    `;
  }
  showToast('پایش هوشمند چندفروشگاهی آغاز شد...', 'gold');

  try {
    const res = await fetch('/api/scrape/run?limit=15', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(`پایش به پایان رسید (${toPersianDigits(data.scraped_offers)} لینک بررسی شد)`, 'emerald');
      await fetchOverview();
      await fetchProducts();
    } else {
      showToast('خطا در پایش: ' + (data.error || 'ناشناخته'), 'ruby');
    }
  } catch (err) {
    showToast('خطا در اتصال به موتور پایش', 'ruby');
  } finally {
    state.isScraping = false;
    if (syncBtn) {
      syncBtn.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
        بروزرسانی قیمت‌ها
      `;
    }
  }
}

// --- Render Functions ---
function renderOverview() {
  const tetherEl = document.getElementById('ticker-tether-val');
  if (tetherEl && state.overview.tether_toman) {
    tetherEl.innerText = `${formatPrice(state.overview.tether_toman)} ت`;
  }

  const statTetherEl = document.getElementById('stat-tether');
  if (statTetherEl && state.overview.tether_toman) {
    statTetherEl.innerText = `${formatPrice(state.overview.tether_toman)} تومان`;
  }

  const syncTimeEl = document.getElementById('stat-last-sync');
  if (syncTimeEl && state.overview.last_sync_time) {
    const dt = new Date(state.overview.last_sync_time);
    syncTimeEl.innerText = dt.toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });
  }

  const prodCountEl = document.getElementById('stat-total-products');
  if (prodCountEl) {
    prodCountEl.innerText = toPersianDigits(state.overview.total_products || state.products.length);
  }

  const backupStatusEl = document.getElementById('backup-status-pill');
  if (backupStatusEl) {
    if (state.overview.cloud_backup_configured) {
      backupStatusEl.innerHTML = `<span class="status-indicator"></span> بک‌آپ ابری فعال`;
      backupStatusEl.style.borderColor = 'rgba(16, 185, 129, 0.4)';
    } else {
      backupStatusEl.innerHTML = `<span class="status-indicator" style="background:#F59E0B;box-shadow:0 0 8px #F59E0B;"></span> بک‌آپ محلی (آماده ذخیره)`;
    }
  }

  // Cheapest store leaderboard highlight
  const leaderContainer = document.getElementById('cheapest-store-highlight');
  if (leaderContainer && state.overview.cheapest_leaderboard && state.overview.cheapest_leaderboard.length) {
    const topStore = state.overview.cheapest_leaderboard[0];
    leaderContainer.innerText = `${topStore.store_name} (${toPersianDigits(topStore.count)} کف قیمت)`;
  }
}

function renderCategoryPills() {
  const container = document.getElementById('category-pills-row');
  if (!container) return;

  const defaultCats = ['همه', '🎯 شکار فرصت‌های آربیتراژ', 'پردازنده', 'کارت گرافیک', 'کولینگ و دیپکول', 'موس و کیبورد گیمینگ', 'رم و اساسدی', 'مادربرد', 'لپتاپ نو و استوک'];
  const allCats = Array.from(new Set([...defaultCats, ...state.categories]));

  container.innerHTML = allCats.map(cat => `
    <button class="category-pill ${state.activeCategory === cat ? 'active' : ''}" onclick="selectCategory('${cat}')">
      ${cat}
    </button>
  `).join('');
}

function selectCategory(cat) {
  if (cat === '🎯 شکار فرصت‌های آربیتراژ') {
    state.huntingOnly = true;
    state.activeCategory = cat;
  } else {
    state.huntingOnly = false;
    state.activeCategory = cat;
  }
  renderCategoryPills();
  fetchProducts();
}

function renderDropdownFilters() {
  const brandSelect = document.getElementById('filter-brand');
  if (brandSelect && state.brands.length) {
    const currentVal = brandSelect.value || state.activeBrand;
    brandSelect.innerHTML = `<option value="همه">همه برندها</option>` +
      state.brands.map(b => `<option value="${b}" ${b === currentVal ? 'selected' : ''}>${b}</option>`).join('');
  }

  const storeSelect = document.getElementById('filter-store');
  if (storeSelect && state.stores.length) {
    const currentVal = storeSelect.value || state.activeStore;
    storeSelect.innerHTML = `<option value="همه">همه فروشگاه‌ها</option>` +
      state.stores.map(s => `<option value="${s}" ${s === currentVal ? 'selected' : ''}>${s}</option>`).join('');
  }
}

function renderProductsGrid() {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  if (state.products.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted); background: var(--surface-card); border-radius: 14px; border: 1px dashed var(--surface-border);">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 12px; color: var(--gold-primary);"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <p style="font-weight: 700; font-size: 1rem;">کالایی با فیلترهای انتخابی یافت نشد.</p>
        <p style="font-size: 0.8rem; margin-top: 6px;">می‌توانید فیلترها را ریست کنید یا کالا و لینک جدید اضافه نمایید.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = state.products.map(p => {
    // Generate mini sparkline SVG
    const sparklineSvg = generateSparkline(p.price_history || []);

    // Change badge
    let changeBadgeHtml = '';
    if (p.change_percent < 0) {
      changeBadgeHtml = `<span class="price-change-badge change-drop">▼ ${toPersianDigits(Math.abs(p.change_percent))}% افت قیمت</span>`;
    } else if (p.change_percent > 0) {
      changeBadgeHtml = `<span class="price-change-badge change-rise">▲ ${toPersianDigits(p.change_percent)}% افزایش</span>`;
    } else {
      changeBadgeHtml = `<span class="price-change-badge change-neutral">ثابت</span>`;
    }

    // Spread & Hunting info
    const isHuntingDeal = p.price_spread_percent >= 3.0 && p.price_spread >= 300000;
    const spreadHtml = p.price_spread > 0 ? `
      <div class="spread-tag" style="${isHuntingDeal ? 'background:rgba(212,175,55,0.15); border:1px solid rgba(212,175,55,0.4); padding:4px 8px; border-radius:6px;' : ''}">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
        ${isHuntingDeal ? '<strong style="color:var(--gold-primary);">🎯 شکار آربیتراژ:</strong> ' : 'اختلاف بازار: '}
        <strong>${formatPrice(p.price_spread)} ت</strong> (${toPersianDigits(p.price_spread_percent)}% سود همکار)
      </div>
    ` : '';

    // Vendor offers list
    const offersHtml = (p.vendor_offers || []).map(o => `
      <div class="offer-row">
        <div>
          <span class="offer-store">${o.store_name}</span>
          <span style="font-size: 0.68rem; margin-right: 6px; color: ${o.in_stock ? '#10B981' : '#EF4444'};">
            ${o.in_stock ? '● موجود' : '○ ناموجود'}
          </span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="offer-price">${formatPrice(o.current_price)} ت</span>
          <a href="${o.product_url}" target="_blank" rel="noopener" class="offer-link-btn">خرید ↗</a>
        </div>
      </div>
    `).join('');

    return `
      <div class="product-card">
        <div>
          <div class="card-header">
            <img src="${p.image_url || 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80'}" alt="${p.name_fa}" class="product-img" onerror="this.src='https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80'">
            <div class="product-meta">
              <span class="condition-badge ${p.condition === 'استوک' ? 'badge-stock' : 'badge-new'}">${p.condition || 'نو'}</span>
              <span style="font-size: 0.7rem; color: var(--gold-light); margin-right: 6px;">${p.brand}</span>
              <h3 class="product-title-fa">${p.name_fa}</h3>
              <p class="product-title-en">${p.name_en || ''}</p>
            </div>
          </div>

          <div class="price-section">
            <div class="lowest-price-row">
              <span class="price-label">کف قیمت بازار:</span>
              <div>
                <span class="lowest-price-val">${formatPrice(p.lowest_price)}</span>
                <span class="toman-unit">تومان</span>
              </div>
            </div>

            <div class="cheapest-store-tag">
              <span>در: <strong class="store-tag-name">${p.lowest_store_name || 'نامشخص'}</strong></span>
              ${changeBadgeHtml}
            </div>
            ${spreadHtml}
          </div>

          <div class="sparkline-container" title="نمودار تغییرات قیمت ۷ روز گذشته">
            ${sparklineSvg}
          </div>

          <div class="offers-accordion">
            <button class="offers-toggle-btn" onclick="toggleOffersList(this)">
              <span>مشاهده قیمت ${toPersianDigits(p.offers_count || p.vendor_offers?.length || 0)} فروشگاه</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div class="offers-list">
              ${offersHtml}
            </div>
          </div>
        </div>

        <div class="card-actions">
          <button class="btn-gold" style="flex: 1; justify-content: center;" onclick="addToQuote(${p.id})">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            + پیش‌فاکتور
          </button>
          <button class="btn-secondary" onclick="openAddOfferModal(${p.id}, '${p.name_fa.replace(/'/g, "\\'")}')" title="افزودن لینک فروشگاه دیگر">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function generateSparkline(history) {
  if (!history || history.length < 2) {
    return `<div style="font-size: 0.68rem; color: var(--text-dim); text-align: center;">داده‌های پایش در حال تکمیل</div>`;
  }

  const prices = history.map(h => h.lowest_price);
  const minP = Math.min(...prices);
  const maxP = Math.max(...prices);
  const range = maxP - minP || 1;

  const width = 280;
  const height = 24;
  const points = prices.map((p, i) => {
    const x = Math.round((i / (prices.length - 1)) * width);
    const y = Math.round(height - ((p - minP) / range) * (height - 6) - 3);
    return `${x},${y}`;
  }).join(' ');

  const strokeColor = prices[prices.length - 1] <= prices[0] ? '#10B981' : '#EF4444';

  return `
    <svg viewBox="0 0 ${width} ${height}" class="sparkline-svg">
      <polyline fill="none" stroke="${strokeColor}" stroke-width="2" points="${points}" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="${points.split(' ').pop().split(',')[0]}" cy="${points.split(' ').pop().split(',')[1]}" r="3" fill="${strokeColor}"/>
    </svg>
  `;
}

function toggleOffersList(btn) {
  const list = btn.nextElementSibling;
  if (!list) return;
  list.classList.toggle('expanded');
  const svg = btn.querySelector('svg');
  if (svg) {
    svg.style.transform = list.classList.contains('expanded') ? 'rotate(180deg)' : 'rotate(0deg)';
  }
}

// --- Quick Quote Builder ---
function addToQuote(productId) {
  const prod = state.products.find(p => p.id === productId);
  if (!prod) return;

  const existing = state.quoteItems.find(item => item.id === prod.id && item.type === 'product');
  if (existing) {
    existing.qty += 1;
  } else {
    state.quoteItems.push({
      id: prod.id,
      type: 'product',
      title: prod.name_fa,
      store: prod.lowest_store_name,
      price: prod.lowest_price,
      qty: 1
    });
  }

  renderQuoteView();
  showToast(`«${prod.name_fa.slice(0, 24)}...» به پیش‌فاکتور افزوده شد.`, 'emerald');
}

function addCustomQuoteRow(title, price, store = 'خدمات/دستی') {
  state.quoteItems.push({
    id: Date.now(),
    type: 'custom',
    title: title,
    store: store,
    price: parseFloat(price) || 0,
    qty: 1
  });
  renderQuoteView();
}

function removeQuoteItem(index) {
  state.quoteItems.splice(index, 1);
  renderQuoteView();
}

function updateQuoteQty(index, delta) {
  if (state.quoteItems[index]) {
    state.quoteItems[index].qty = Math.max(1, state.quoteItems[index].qty + delta);
    renderQuoteView();
  }
}

function renderQuoteView() {
  const container = document.getElementById('quote-items-list');
  const badge = document.getElementById('nav-quote-badge');
  if (badge) {
    const totalCount = state.quoteItems.reduce((acc, i) => acc + i.qty, 0);
    badge.innerText = toPersianDigits(totalCount);
    badge.style.display = totalCount > 0 ? 'inline-block' : 'none';
  }

  if (!container) return;

  if (state.quoteItems.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 36px; color: var(--text-muted);">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 10px; color: var(--gold-primary);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <p style="font-weight: 700;">پیش‌فاکتور خالی است.</p>
        <p style="font-size: 0.78rem; margin-top: 4px;">با زدن دکمه «+ پیش‌فاکتور» روی هر کالا یا استفاده از دکمه‌های خدمات زیر، سیستم را اسمبل کنید.</p>
      </div>
    `;
    updateQuoteCalculations(0);
    return;
  }

  let subtotal = 0;
  container.innerHTML = state.quoteItems.map((item, idx) => {
    const lineTotal = item.price * item.qty;
    subtotal += lineTotal;
    return `
      <div class="quote-item-row">
        <div style="flex-grow: 1;">
          <strong style="font-size: 0.88rem; display: block;">${item.title}</strong>
          <span style="font-size: 0.72rem; color: var(--text-dim);">${item.store} • واحد: ${formatPrice(item.price)} ت</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <div style="display: flex; align-items: center; background: var(--surface-elevated); border-radius: 6px; border: 1px solid var(--surface-border);">
            <button onclick="updateQuoteQty(${idx}, -1)" style="background:transparent;border:none;color:var(--text-main);padding:2px 8px;cursor:pointer;">-</button>
            <span style="font-size: 0.8rem; font-weight: 700; padding: 0 4px;">${toPersianDigits(item.qty)}</span>
            <button onclick="updateQuoteQty(${idx}, 1)" style="background:transparent;border:none;color:var(--text-main);padding:2px 8px;cursor:pointer;">+</button>
          </div>
          <span style="font-weight: 700; font-size: 0.88rem; min-width: 90px; text-align: left; color: var(--gold-light);">${formatPrice(lineTotal)} ت</span>
          <button onclick="removeQuoteItem(${idx})" style="background:transparent;border:none;color:#EF4444;cursor:pointer;padding:4px;" title="حذف ردیف">✕</button>
        </div>
      </div>
    `;
  }).join('');

  updateQuoteCalculations(subtotal);
}

function updateQuoteCalculations(subtotal) {
  const marginPercent = parseFloat(state.quoteMarginPercent) || 0;
  const marginAmount = Math.round(subtotal * (marginPercent / 100));
  const discount = parseFloat(state.quoteColleagueDiscount) || 0;
  const grandTotal = Math.max(0, subtotal + marginAmount - discount);

  const subtotalEl = document.getElementById('quote-subtotal-val');
  if (subtotalEl) subtotalEl.innerText = `${formatPrice(subtotal)} تومان`;

  const marginValEl = document.getElementById('quote-margin-val');
  if (marginValEl) marginValEl.innerText = `${formatPrice(marginAmount)} تومان (${toPersianDigits(marginPercent)}٪)`;

  const totalEl = document.getElementById('quote-grand-total-val');
  if (totalEl) totalEl.innerText = `${formatPrice(grandTotal)} تومان`;
}

function copyQuoteForCustomer() {
  if (state.quoteItems.length === 0) {
    showToast('پیش‌فاکتوری برای کپی وجود ندارد.', 'ruby');
    return;
  }

  let subtotal = 0;
  const itemsText = state.quoteItems.map((item, idx) => {
    const lineTotal = item.price * item.qty;
    subtotal += lineTotal;
    return `${toPersianDigits(idx + 1)}. ${item.title} (تعداد: ${toPersianDigits(item.qty)}) ── ${formatPrice(lineTotal)} تومان`;
  }).join('\n');

  const marginPercent = parseFloat(state.quoteMarginPercent) || 0;
  const marginAmount = Math.round(subtotal * (marginPercent / 100));
  const discount = parseFloat(state.quoteColleagueDiscount) || 0;
  const grandTotal = Math.max(0, subtotal + marginAmount - discount);

  const quoteText = `
═══════════════════════
✦ پیش‌فاکتور رسمی سخت‌افزار و قطعات ✦
فروشگاه و کارگاه تخصصی اوراتک (AuraTech)
═══════════════════════
${itemsText}

───────────────────────
🔹 جمع کل قطعات: ${formatPrice(subtotal)} تومان
${marginAmount > 0 ? `🔹 خدمات، اسمبل و گارانتی: ${formatPrice(marginAmount)} تومان\n` : ''}${discount > 0 ? `🔹 تخفیف همکاری ویژه: ${formatPrice(discount)} تومان\n` : ''}💎 مبلغ نهایی قابل پرداخت: ${formatPrice(grandTotal)} تومان
───────────────────────
✓ تمام قطعات دارای مهلت تست و گارانتی معتبر شرکتی می‌باشند.
✓ قیمت‌ها بر اساس لحظه‌ای‌ترین نرخ بازار و ارز محاسبه شده‌اند.
═══════════════════════
  `.trim();

  navigator.clipboard.writeText(quoteText).then(() => {
    showToast('پیش‌فاکتور با فرمت مناسب در کلیپ‌بورد کپی شد (آماده ارسال در واتساپ/تلگرام)', 'emerald');
  }).catch(() => {
    showToast('خطا در کپی در کلیپ‌بورد', 'ruby');
  });
}

function clearQuote() {
  state.quoteItems = [];
  renderQuoteView();
  showToast('پیش‌فاکتور پاک شد.', 'gold');
}

// --- Watchlist Manager & Live URL Tester ---
async function testScraperUrl() {
  const urlInput = document.getElementById('test-url-input');
  const selectorInput = document.getElementById('test-selector-input');
  const resultBox = document.getElementById('test-url-result');
  const url = urlInput?.value?.trim();

  if (!url) {
    showToast('لطفاً آدرس کالا را وارد نمایید.', 'ruby');
    return;
  }

  resultBox.style.display = 'block';
  resultBox.innerHTML = `
    <div style="display:flex;align-items:center;gap:8px;color:var(--gold-light);">
      <svg class="spin-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
      در حال تحلیل آبشاری ۴ لایه و استخراج زنده قیمت...
    </div>
  `;

  try {
    const res = await fetch('/api/scraper/test-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url, custom_selector: selectorInput?.value?.trim() || null })
    });
    const data = await res.json();

    if (data.success && data.price > 0) {
      resultBox.innerHTML = `
        <div style="background:var(--surface-elevated);border:1px solid #10B981;border-radius:10px;padding:14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <strong style="color:#10B981;">✓ استخراج موفقیت‌آمیز</strong>
            <span style="font-size:0.75rem;background:rgba(212,175,55,0.15);color:var(--gold-primary);padding:2px 8px;border-radius:4px;">${data.layer || 'پایش خودکار'}</span>
          </div>
          <div style="font-size:0.9rem;margin-bottom:6px;"><strong>فروشگاه:</strong> ${data.store_name}</div>
          <div style="font-size:0.85rem;margin-bottom:8px;color:var(--text-muted);"><strong>عنوان کالا:</strong> ${data.title || 'تشخیص داده شد'}</div>
          <div style="font-size:1.2rem;font-weight:800;color:var(--gold-primary);margin-bottom:6px;">قیمت استخراجی: ${formatPrice(data.price)} تومان</div>
          <div style="font-size:0.75rem;color:${data.in_stock ? '#10B981' : '#EF4444'};">وضعیت: ${data.in_stock ? 'موجود در انبار' : 'ناموجود'}</div>
        </div>
      `;

      // Pre-fill modal fields if empty
      const nameInput = document.getElementById('prod-name-fa');
      if (nameInput && !nameInput.value && data.title) {
        nameInput.value = data.title;
      }
      const priceInput = document.getElementById('prod-initial-price');
      if (priceInput) priceInput.value = data.price;
    } else {
      resultBox.innerHTML = `
        <div style="background:var(--surface-elevated);border:1px solid #EF4444;border-radius:10px;padding:12px;color:#EF4444;">
          ✕ ${data.error || 'قیمت از این آدرس استخراج نشد. لطفاً سلکتور دستی وارد کنید یا آدرس را بررسی نمایید.'}
        </div>
      `;
    }
  } catch (err) {
    resultBox.innerHTML = `<div style="color:#EF4444;">خطا در ارسال درخواست به سرور پایش</div>`;
  }
}

async function saveNewProduct(e) {
  e.preventDefault();
  const name_fa = document.getElementById('prod-name-fa')?.value?.trim();
  const name_en = document.getElementById('prod-name-en')?.value?.trim();
  const category = document.getElementById('prod-category')?.value;
  const brand = document.getElementById('prod-brand')?.value?.trim();
  const condition = document.getElementById('prod-condition')?.value;
  const image_url = document.getElementById('prod-image-url')?.value?.trim();
  const url = document.getElementById('test-url-input')?.value?.trim();
  const price = parseFloat(document.getElementById('prod-initial-price')?.value) || 0;

  if (!name_fa || !category || !brand) {
    showToast('لطفاً عنوان، دسته‌بندی و برند را تکمیل کنید.', 'ruby');
    return;
  }

  const payload = {
    name_fa: name_fa,
    name_en: name_en,
    category: category,
    brand: brand,
    condition: condition,
    image_url: image_url || null,
    initial_offer: url ? {
      product_url: url,
      current_price: price > 0 ? price : null
    } : null
  };

  try {
    const res = await fetch('/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      showToast('کالای جدید با موفقیت به دیده‌بان افزوده شد.', 'emerald');
      document.getElementById('new-product-form')?.reset();
      document.getElementById('test-url-result').style.display = 'none';
      await fetchOverview();
      await fetchProducts();
      switchTab('market');
    }
  } catch (err) {
    showToast('خطا در ذخیره کالا', 'ruby');
  }
}

function renderManageProductsList() {
  const container = document.getElementById('manage-products-list');
  if (!container) return;

  container.innerHTML = state.products.map(p => `
    <div style="background:var(--surface-elevated);border:1px solid var(--surface-border);border-radius:10px;padding:12px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
      <div>
        <strong style="font-size:0.9rem;">${p.name_fa}</strong>
        <div style="font-size:0.75rem;color:var(--text-dim);margin-top:2px;">
          ${p.brand} • ${p.category} • ${toPersianDigits(p.offers_count)} فروشگاه متصل • کف: ${formatPrice(p.lowest_price)} ت
        </div>
      </div>
      <div style="display:flex;gap:8px;">
        <button class="btn-secondary" onclick="openAddOfferModal(${p.id}, '${p.name_fa.replace(/'/g, "\\'")}')" style="font-size:0.75rem;">+ لینک فروشگاه</button>
        <button class="btn-secondary" onclick="deleteProduct(${p.id})" style="color:#EF4444;border-color:rgba(239,68,68,0.3);font-size:0.75rem;">حذف کالا</button>
      </div>
    </div>
  `).join('');
}

async function deleteProduct(id) {
  if (!confirm('آیا از حذف این کالا و تمام لینک‌های متصل به آن مطمئن هستید؟')) return;
  try {
    const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('کالا با موفقیت حذف شد.', 'gold');
      await fetchOverview();
      await fetchProducts();
    }
  } catch (err) {
    showToast('خطا در حذف کالا', 'ruby');
  }
}

// --- Add Offer Modal ---
let targetProductIdForOffer = null;
function openAddOfferModal(prodId, prodName) {
  targetProductIdForOffer = prodId;
  const modal = document.getElementById('modal-add-offer');
  const titleEl = document.getElementById('modal-offer-prod-title');
  if (titleEl) titleEl.innerText = prodName;
  if (modal) modal.classList.add('active');
}
function closeAddOfferModal() {
  const modal = document.getElementById('modal-add-offer');
  if (modal) modal.classList.remove('active');
  targetProductIdForOffer = null;
}

async function submitNewOffer(e) {
  e.preventDefault();
  if (!targetProductIdForOffer) return;
  const url = document.getElementById('modal-offer-url')?.value?.trim();
  const store = document.getElementById('modal-offer-store')?.value?.trim();
  const selector = document.getElementById('modal-offer-selector')?.value?.trim();

  if (!url) {
    showToast('آدرس کالا الزامی است.', 'ruby');
    return;
  }

  try {
    const res = await fetch(`/api/products/${targetProductIdForOffer}/offers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_url: url,
        store_name: store || null,
        custom_css_selector: selector || null
      })
    });
    if (res.ok) {
      showToast('لینک فروشگاه افزوده و پایش شد.', 'emerald');
      closeAddOfferModal();
      await fetchProducts();
    }
  } catch (err) {
    showToast('خطا در افزودن لینک', 'ruby');
  }
}

// --- Backup & Cloud Sync Vault ---
async function uploadRestoreBackup(input) {
  const file = input.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('mode', 'replace');

  showToast('در حال بازیابی اطلاعات پایگاه داده...', 'gold');
  try {
    const res = await fetch('/api/backup/import-json', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message || 'بازیابی با موفقیت کامل انجام شد!', 'emerald');
      await fetchOverview();
      await fetchProducts();
    } else {
      showToast('خطا در بازیابی: ' + (data.detail || data.error), 'ruby');
    }
  } catch (err) {
    showToast('خطا در ارسال فایل پشتیبان', 'ruby');
  }
}

async function saveCloudSettings(e) {
  e.preventDefault();
  const token = document.getElementById('setting-gist-token')?.value?.trim();
  const gistId = document.getElementById('setting-gist-id')?.value?.trim();
  const autoSync = document.getElementById('setting-auto-sync')?.checked ? 'true' : 'false';

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        github_backup_token: token || null,
        github_gist_id: gistId || null,
        auto_sync_gist: autoSync
      })
    });
    if (res.ok) {
      showToast('تنظیمات گیت‌هاب با موفقیت ذخیره شدند.', 'emerald');
      await fetchOverview();
    }
  } catch (err) {
    showToast('خطا در ذخیره تنظیمات', 'ruby');
  }
}

async function triggerGistSyncNow() {
  showToast('در حال همگام‌سازی ابری با GitHub Gist...', 'gold');
  try {
    const res = await fetch('/api/backup/cloud-sync', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'emerald');
      if (data.gist_id) {
        const idInput = document.getElementById('setting-gist-id');
        if (idInput) idInput.value = data.gist_id;
      }
      await fetchOverview();
    } else {
      showToast('خطا: ' + (data.error || 'عدم دسترسی به گیت‌هاب'), 'ruby');
    }
  } catch (err) {
    showToast('خطای ارتباط با سرور', 'ruby');
  }
}

async function triggerGistRestoreNow() {
  if (!confirm('آیا مایلید تمام اطلاعات فعلی با آخرین نسخه پشتیبان گیت‌هاب جایگزین شود؟')) return;
  showToast('در حال فراخوانی فایل بک‌آپ از GitHub Gist...', 'gold');
  try {
    const res = await fetch('/api/backup/cloud-restore', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(`دیتابیس با موفقیت از گست ابری بازیابی شد (${toPersianDigits(data.restored_products)} کالا)`, 'emerald');
      await fetchOverview();
      await fetchProducts();
    } else {
      showToast('خطا در بازیابی: ' + (data.error || 'یافت نشد'), 'ruby');
    }
  } catch (err) {
    showToast('خطا در اتصال به گیت‌هاب', 'ruby');
  }
}

function copyCronUrl() {
  const url = `${window.location.origin}/api/cron/trigger`;
  navigator.clipboard.writeText(url).then(() => {
    showToast('آدرس وبهوک کرون‌جاب در کلیپ‌بورد کپی شد!', 'emerald');
  });
}

// --- Event Listeners Setup ---
document.addEventListener('DOMContentLoaded', () => {
  // Initial Loads
  fetchOverview();
  fetchProducts();

  // Search input with debounce
  let searchTimeout = null;
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        state.searchQuery = e.target.value;
        fetchProducts();
      }, 300);
    });
  }

  // Brand & Store filter dropdowns
  const brandSelect = document.getElementById('filter-brand');
  if (brandSelect) {
    brandSelect.addEventListener('change', (e) => {
      state.activeBrand = e.target.value;
      fetchProducts();
    });
  }

  const storeSelect = document.getElementById('filter-store');
  if (storeSelect) {
    storeSelect.addEventListener('change', (e) => {
      state.activeStore = e.target.value;
      fetchProducts();
    });
  }

  const sortSelect = document.getElementById('filter-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.activeSort = e.target.value;
      fetchProducts();
    });
  }

  const conditionSelect = document.getElementById('filter-condition');
  if (conditionSelect) {
    conditionSelect.addEventListener('change', (e) => {
      state.activeCondition = e.target.value;
      fetchProducts();
    });
  }

  // Margin slider listener
  const slider = document.getElementById('quote-margin-slider');
  const sliderDisplay = document.getElementById('quote-margin-display');
  if (slider) {
    slider.addEventListener('input', (e) => {
      state.quoteMarginPercent = e.target.value;
      if (sliderDisplay) sliderDisplay.innerText = `${toPersianDigits(e.target.value)}٪`;
      renderQuoteView();
    });
  }

  const discountInput = document.getElementById('quote-discount-input');
  if (discountInput) {
    discountInput.addEventListener('input', (e) => {
      state.quoteColleagueDiscount = parseFloat(e.target.value) || 0;
      renderQuoteView();
    });
  }

  // Auto-fill Cron Webhook URL on settings page
  const cronUrlDisplay = document.getElementById('cron-webhook-url');
  if (cronUrlDisplay) {
    cronUrlDisplay.innerText = `${window.location.origin}/api/cron/trigger`;
  }

  // Load existing settings into inputs
  fetch('/api/settings').then(res => res.json()).then(sett => {
    if (sett.github_backup_token) {
      const tInput = document.getElementById('setting-gist-token');
      if (tInput) tInput.value = sett.github_backup_token;
    }
    if (sett.github_gist_id) {
      const gInput = document.getElementById('setting-gist-id');
      if (gInput) gInput.value = sett.github_gist_id;
    }
    if (sett.auto_sync_gist) {
      const aInput = document.getElementById('setting-auto-sync');
      if (aInput) aInput.checked = (sett.auto_sync_gist.toLowerCase() === 'true');
    }
  }).catch(() => {});
});
