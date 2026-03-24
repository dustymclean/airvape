import csv
import json
import os
import re

CSV_PATH = os.path.expanduser("~/Desktop/AirVape_Scraper/airvape_enriched_catalog.csv")
OUTPUT_DIR = os.path.expanduser("~/Desktop/AirVape_Shop")

def slugify(text):
    text = str(text).lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def ensure_dirs():
    os.makedirs(os.path.join(OUTPUT_DIR, "css"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "js"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "categories"), exist_ok=True)

def generate_site():
    ensure_dirs()
    if not os.path.exists(CSV_PATH):
        print(f"File not found: {CSV_PATH}")
        return
        
    products_map = {}
    
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle = row["Handle"]
            # Exclude items with no matching Shopify data entirely, or if price is missing
            if row["Match Confidence"] == "None" or not row["Variant Price"]:
                continue
                
            if handle not in products_map:
                products_map[handle] = {
                    "handle": handle,
                    "brand": row["Brand"] or "AirVape",
                    "title": row["Title"],
                    "body_html": row["Body (HTML)"],
                    "all_images": [img for img in row["All Images"].split(" | ") if img],
                    "featured_image": "",
                    "min_price": float(row["Variant Price"]) if row["Variant Price"] else 0.0,
                    "options": [{"name": row["Option1 Name"] or "Options"}],
                    "in_stock_variants": []
                }
                if products_map[handle]["all_images"]:
                    products_map[handle]["featured_image"] = products_map[handle]["all_images"][0]
            
            # Variant
            try:
                price = float(row["Variant Price"])
            except:
                price = 0.0
                
            if price < products_map[handle]["min_price"]:
                products_map[handle]["min_price"] = price
                
            products_map[handle]["in_stock_variants"].append({
                "option1_value": row["Option1 Value"] or "Default",
                "price": price,
                "variant_image": row["Variant Image"] or products_map[handle]["featured_image"],
                "sku": row["SKU"]
            })
            
    products = list(products_map.values())
    print(f"Loaded {len(products)} products.")
    
    # Organize products
    brands = {"AirVape": []}
    categories = {}
    
    for p in products:
        b = p.get("brand", "AirVape")
        if b not in brands:
            brands[b] = []
        brands[b].append(p)
            
        ptype = "Vaporizers" if "vaporizer" in p["title"].lower() else "Accessories"
        if b not in categories:
            categories[b] = {}
        if ptype not in categories[b]:
            categories[b][ptype] = []
        categories[b][ptype].append(p)
    
    # CSS
    css_content = """
    :root { --primary: #111; --gold: #d4af37; --bg: #fff; --muted: #888; --border: #eaeaea; --sidebar-w: 260px; }
    body { font-family: 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: var(--primary); margin: 0; padding: 0; }
    .sidebar { position: fixed; width: var(--sidebar-w); left: 0; top: 0; bottom: 0; background: #fafafa; border-right: 1px solid var(--border); overflow-y: auto; padding: 30px 20px; box-sizing: border-box; }
    .sidebar-logo { font-size: 22px; font-weight: 800; text-decoration: none; color: #000; display: block; margin-bottom: 5px; }
    .sidebar-tagline { font-size: 11px; text-transform: uppercase; color: var(--muted); letter-spacing: 1px; margin-bottom: 30px; }
    .sidebar-section { font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin: 20px 0 10px; color: var(--muted); }
    .sidebar-link { display: block; padding: 6px 0; color: #333; text-decoration: none; font-size: 14px; font-weight: 500; }
    .sidebar-link:hover, .sidebar-link.active { color: var(--gold); }
    .sidebar-link.child { padding-left: 15px; font-size: 13px; color: #555; }
    .sidebar-footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); }
    
    .sidebar-community { margin-top: 30px; padding: 15px; background: #111; color: #fff; border-radius: 8px; }
    .sidebar-community h4 { margin: 0 0 10px; font-size: 12px; color: var(--gold); text-transform: uppercase; }
    .sidebar-community p { font-size: 11px; line-height: 1.4; margin: 0 0 10px; color: #ccc; }
    .sidebar-community a.link { color: #fff; font-size: 11px; text-decoration: underline; display: block; margin-bottom: 10px; }
    
    .main-wrapper { margin-left: var(--sidebar-w); min-height: 100vh; display: flex; flex-direction: column; }
    .main-content { padding: 40px 50px; flex: 1; }
    
    .page-title { font-size: 32px; font-weight: 800; margin: 0 0 10px; }
    .page-subtitle { color: var(--muted); margin-bottom: 40px; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; }
    .card { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; background: #fff; transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; cursor: pointer; }
    .card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: #ddd; }
    .card-img { width: 100%; height: 280px; object-fit: contain; padding: 20px; box-sizing: border-box; background: #fdfdfd; border-bottom: 1px solid var(--border); }
    .card-body { padding: 20px; flex: 1; display: flex; flex-direction: column; }
    .card-brand { font-size: 11px; text-transform: uppercase; color: var(--muted); letter-spacing: 1px; margin-bottom: 5px; }
    .card-title { font-size: 16px; font-weight: 600; margin: 0 0 10px; flex: 1; line-height: 1.4; }
    .card-price { font-size: 18px; font-weight: 700; color: var(--gold); margin-bottom: 15px; }
    
    .btn { display: inline-block; background: #000; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 700; text-transform: uppercase; text-align: center; border: none; cursor: pointer; transition: background 0.2s; }
    .btn:hover { background: var(--gold); color: #000; }
    .btn-outline { background: transparent; color: #000; border: 1px solid #000; }
    .btn-outline:hover { background: #000; color: #fff; }
    .btn-danger { background: #ff4444; color: #fff; }
    .btn-danger:hover { background: #cc0000; }
    
    .input-box { margin-bottom: 15px; text-align: left; }
    .input-box label { display: block; font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 6px; }
    .input-box input { width: 100%; border: 1px solid var(--border); padding: 10px; border-radius: 6px; box-sizing: border-box; font-family: inherit; }
    
    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: none; align-items: center; justify-content: center; backdrop-filter: blur(4px); }
    .modal-overlay.active { display: flex; }
    .modal { background: #fff; width: 90%; max-width: 1000px; max-height: 90vh; border-radius: 16px; display: flex; overflow: hidden; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.2); }
    .modal-close { position: absolute; top: 20px; right: 20px; background: #f0f0f0; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 20px; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; }
    .modal-close:hover { background: #e0e0e0; }
    
    .modal-left { width: 50%; background: #fdfdfd; padding: 40px; border-right: 1px solid var(--border); position: relative; }
    .modal-main-img { width: 100%; height: 400px; object-fit: contain; margin-bottom: 20px; }
    .modal-right { width: 50%; padding: 40px; overflow-y: auto; max-height: 90vh; }
    .modal-brand { font-size: 12px; text-transform: uppercase; color: var(--muted); letter-spacing: 1px; margin-bottom: 5px; }
    .modal-title { font-size: 28px; font-weight: 800; margin: 0 0 15px; }
    .modal-price { font-size: 24px; font-weight: 700; color: var(--gold); margin-bottom: 25px; }
    .modal-desc { font-size: 15px; line-height: 1.6; color: #444; margin-bottom: 30px; }
    .modal-desc p { margin-top: 0; }
    .variant-label { font-size: 12px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; display: block; }
    .swatch-group { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 30px; }
    .swatch { border: 1px solid #ddd; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; background: #fff; transition: all 0.2s; }
    .swatch:hover { border-color: #aaa; }
    .swatch.selected { border-color: #000; background: #000; color: #fff; }
    .modal-buy-btn { width: 100%; padding: 15px; font-size: 15px; border-radius: 8px; }
    
    .site-footer { background-color: #000; color: #fff; padding: 80px 50px 30px; margin-top: 80px; font-family: 'Helvetica Neue', Arial, sans-serif; }
    .footer-content { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; gap: 50px; max-width: 1400px; margin: 0 auto; border-bottom: 1px solid #222; padding-bottom: 60px; }
    .footer-col h3 { color: #fff; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; margin: 0 0 25px; }
    .footer-col p { color: #888; font-size: 13px; line-height: 1.8; margin: 0 0 10px; }
    .footer-col ul { list-style: none; padding: 0; margin: 0; }
    .footer-col ul li { margin-bottom: 15px; }
    .footer-col ul li a { color: #888; text-decoration: none; font-size: 13px; transition: 0.3s; }
    .footer-col ul li a:hover { color: var(--gold); }
    .newsletter-form { display: flex; flex-direction: column; gap: 15px; margin-top: 20px; }
    .newsletter-form input { padding: 15px; background: #111; border: 1px solid #333; color: #fff; border-radius: 6px; outline: none; font-family: inherit; }
    .newsletter-form input:focus { border-color: var(--gold); }
    .newsletter-form button { padding: 15px; background: var(--gold); color: #000; border: none; border-radius: 6px; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; font-family: inherit; }
    .newsletter-form button:hover { background: #fff; }
    .footer-bottom { display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 30px auto 0; font-size: 11px; color: #666; letter-spacing: 1px; text-transform: uppercase; font-weight: 800; }
    .footer-socials { display: flex; gap: 20px; }
    .footer-socials a { color: #888; text-decoration: none; transition: 0.3s; }
    .footer-socials a:hover { color: var(--gold); }
    
    @media (max-width: 992px) {
        .site-footer { padding: 60px 30px 30px; }
        .footer-content { grid-template-columns: 1fr 1fr; gap: 40px; }
        .footer-bottom { flex-direction: column; gap: 20px; text-align: center; }
    }
    @media (max-width: 600px) {
        .footer-content { grid-template-columns: 1fr; gap: 40px; }
    }

    .age-gate-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: #000; z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 20px; }
    .age-gate-box { max-width: 480px; width: 100%; text-align: center; }
    .age-gate-logo { font-size: 28px; font-weight: 900; color: #fff; letter-spacing: -1px; margin-bottom: 8px; }
    .age-gate-logo span { color: var(--gold); }
    .age-gate-tagline { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #888; margin-bottom: 50px; }
    .age-gate-heading { font-size: 13px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; color: #888; margin-bottom: 15px; }
    .age-gate-title { font-size: 38px; font-weight: 900; color: #fff; margin: 0 0 20px; line-height: 1.1; }
    .age-gate-subtitle { font-size: 15px; color: #888; line-height: 1.6; margin-bottom: 40px; }
    .age-gate-buttons { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
    .age-gate-yes { background: var(--gold); color: #000; border: none; padding: 16px 40px; font-size: 14px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
    .age-gate-yes:hover { background: #fff; }
    .age-gate-no { background: transparent; color: #555; border: 1px solid #333; padding: 16px 40px; font-size: 14px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
    .age-gate-no:hover { border-color: #555; color: #888; }
    .age-gate-disclaimer { font-size: 11px; color: #444; margin-top: 30px; line-height: 1.6; }

    .banner { background: #000; color: #fff; text-align: center; padding: 10px; font-size: 11px; font-weight: 900; letter-spacing: 2px; position: fixed; top: 0; left: 0; right: 0; z-index: 1000; text-transform: uppercase; border-bottom: 2px solid var(--gold); }
    .banner a { color: var(--gold); text-decoration: none; transition: 0.3s; }
    .banner a:hover { color: #fff; }
    .sidebar { top: 36px; }
    .main-wrapper { margin-top: 36px; }
    @media (max-width: 900px) { .sidebar { top: 0; } }

    .cart-float { position: fixed; bottom: 30px; right: 30px; background: #000; color: #fff; width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; box-shadow: 0 10px 25px rgba(0,0,0,0.3); z-index: 900; transition: transform 0.2s; border: 2px solid var(--gold); }
    .cart-float:hover { transform: scale(1.05); }
    .cart-badge { position: absolute; top: -5px; right: -5px; background: red; color: white; font-size: 13px; font-weight: bold; width: 24px; height: 24px; border-radius: 50%; display: none; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
    
    .cart-modal { max-width: 600px; width: 100%; flex-direction: column; padding: 30px; }
    .cart-items-container { overflow-y: auto; max-height: 50vh; margin-top: 20px; margin-bottom: 20px; padding-right: 10px; }
    .cart-item { display: flex; align-items: center; border-bottom: 1px solid var(--border); padding: 15px 0; }
    .cart-item-img { width: 60px; height: 60px; object-fit: contain; background: #fdfdfd; border: 1px solid var(--border); border-radius: 6px; margin-right: 15px; }
    .cart-item-info { flex: 1; }
    .cart-item-title { font-size: 14px; font-weight: bold; margin: 0 0 5px; }
    .cart-item-variant { font-size: 12px; color: var(--muted); margin: 0 0 5px; }
    .cart-item-price { font-size: 14px; font-weight: bold; color: var(--gold); }
    .cart-item-controls { display: flex; align-items: center; gap: 10px; }
    .qty-btn { background: #eee; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; font-weight: bold; display:flex; align-items:center; justify-content:center; }
    .qty-btn:hover { background: #ddd; }
    .remove-btn { color: red; background: none; border: none; cursor: pointer; font-size: 12px; text-decoration: underline; padding: 5px; }
    .cart-total-row { display: flex; justify-content: space-between; align-items: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; border-top: 2px solid #000; padding-top: 20px; }
    
    @media (max-width: 900px) {
        .sidebar { transform: translateX(-100%); z-index: 100; transition: transform 0.3s; }
        .main-wrapper { margin-left: 0; }
        .modal { flex-direction: column; overflow-y: auto; }
        .modal-left, .modal-right { width: 100%; }
        .modal-left { border-right: none; border-bottom: 1px solid var(--border); padding: 20px; }
        .modal-main-img { height: 300px; }
        .modal-right { max-height: none; padding: 20px; }
        .cart-float { bottom: 20px; right: 20px; }
    }
    """
    with open(os.path.join(OUTPUT_DIR, "css", "style.css"), "w") as f:
        f.write(css_content)
        
    js_content = """
    document.addEventListener('DOMContentLoaded', () => {
        let cart = JSON.parse(localStorage.getItem('pixies_cart')) || [];
        
        const modalOverlay = document.getElementById('modal-overlay');
        const modalClose = document.getElementById('modal-close');
        
        const cartOverlay = document.getElementById('cart-overlay');
        const cartClose = document.getElementById('cart-close');
        
        const checkoutOverlay = document.getElementById('checkout-overlay');
        const checkoutClose = document.getElementById('checkout-close');
        
        const mBrand = document.getElementById('m-brand');
        const mTitle = document.getElementById('m-title');
        const mPrice = document.getElementById('m-price');
        const mDesc = document.getElementById('m-desc');
        const mImg = document.getElementById('m-img');
        const swatchesContainer = document.getElementById('swatches');
        const vLabel = document.getElementById('v-label');
        const addToCartBtn = document.getElementById('add-to-cart-btn');
        
        const cartFloat = document.getElementById('cart-float');
        const cartBadge = document.getElementById('cart-badge');
        const cartItemsContainer = document.getElementById('cart-items-container');
        const cartTotalEl = document.getElementById('cart-total');
        const proceedToCheckoutBtn = document.getElementById('proceed-checkout-btn');
        
        const checkoutForm = document.getElementById('checkout-form');
        const checkoutItemDesc = document.getElementById('checkout-item-desc');
        const checkoutFeedback = document.getElementById('checkout-feedback');
        const cSubmit = document.getElementById('c_submit');
        
        let currentCheckoutItem = null;
        
        function updateCart() {
            localStorage.setItem('pixies_cart', JSON.stringify(cart));
            cartItemsContainer.innerHTML = '';
            
            let totalQty = 0;
            let totalPrice = 0;
            
            if(cart.length === 0) {
                cartItemsContainer.innerHTML = '<p style="text-align:center; color:#888; margin: 40px 0;">Your cart is completely empty. Add some gear!</p>';
                proceedToCheckoutBtn.style.display = 'none';
                cartBadge.style.display = 'none';
                cartTotalEl.textContent = '$0.00';
                return;
            }
            
            proceedToCheckoutBtn.style.display = 'block';
            
            cart.forEach((item, index) => {
                totalQty += item.qty;
                totalPrice += item.price * item.qty;
                
                const itemEl = document.createElement('div');
                itemEl.className = 'cart-item';
                itemEl.innerHTML = `
                    <img src="${item.image}" class="cart-item-img" alt="${item.title}">
                    <div class="cart-item-info">
                        <div class="cart-item-title">${item.title}</div>
                        <div class="cart-item-variant">${item.variant}</div>
                        <div class="cart-item-price">$${parseFloat(item.price).toFixed(2)}</div>
                    </div>
                    <div class="cart-item-controls">
                        <button class="qty-btn" onclick="changeQty(${index}, -1)">-</button>
                        <span>${item.qty}</span>
                        <button class="qty-btn" onclick="changeQty(${index}, 1)">+</button>
                        <button class="remove-btn" onclick="removeFromCart(${index})">Remove</button>
                    </div>
                `;
                cartItemsContainer.appendChild(itemEl);
            });
            
            cartBadge.textContent = totalQty;
            cartBadge.style.display = 'flex';
            cartTotalEl.textContent = '$' + totalPrice.toFixed(2);
        }
        
        window.changeQty = (index, delta) => {
            cart[index].qty += delta;
            if(cart[index].qty <= 0) cart.splice(index, 1);
            updateCart();
        };
        
        window.removeFromCart = (index) => {
            cart.splice(index, 1);
            updateCart();
        };
        
        cartFloat.onclick = () => {
            updateCart();
            cartOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        };
        
        cartClose.onclick = () => {
            cartOverlay.classList.remove('active');
            document.body.style.overflow = '';
        };
        
        window.openModal = function(handle) {
            const p = window.productsData[handle];
            if(!p) return;
            
            mBrand.textContent = p.brand;
            mTitle.textContent = p.title;
            mPrice.textContent = '$' + p.min_price.toFixed(2);
            mDesc.innerHTML = p.body_html || 'No description available.';
            
            const firstVariant = p.in_stock_variants[0];
            mImg.src = firstVariant.variant_image || p.featured_image || 'https://via.placeholder.com/400';
            
            currentCheckoutItem = {
                title: p.title,
                brand: p.brand,
                variant: firstVariant.option1_value || 'Default',
                price: parseFloat(firstVariant.price)
            };
            
            swatchesContainer.innerHTML = '';
            vLabel.textContent = p.options[0] ? p.options[0].name : 'Options';
            
            if(p.in_stock_variants.length > 0) {
                p.in_stock_variants.forEach((v, idx) => {
                    const btn = document.createElement('button');
                    btn.className = 'swatch' + (idx === 0 ? ' selected' : '');
                    btn.textContent = v.option1_value || 'Default';
                    btn.onclick = () => {
                        document.querySelectorAll('.swatch').forEach(s => s.classList.remove('selected'));
                        btn.classList.add('selected');
                        if(v.variant_image) mImg.src = v.variant_image;
                        const vPrice = parseFloat(v.price);
                        mPrice.textContent = '$' + vPrice.toFixed(2);
                        currentCheckoutItem.variant = v.option1_value || 'Default';
                        currentCheckoutItem.price = vPrice;
                    };
                    swatchesContainer.appendChild(btn);
                });
                addToCartBtn.style.display = 'block';
            } else {
                swatchesContainer.innerHTML = '<span class="muted">Out of stock</span>';
                addToCartBtn.style.display = 'none';
            }
            
            modalOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        };
        
        modalClose.onclick = () => {
            modalOverlay.classList.remove('active');
            document.body.style.overflow = '';
        };
        
        addToCartBtn.onclick = () => {
            if(!currentCheckoutItem) return;
            
            const existingIndex = cart.findIndex(i => i.title === currentCheckoutItem.title && i.variant === currentCheckoutItem.variant);
            if(existingIndex > -1) {
                cart[existingIndex].qty += 1;
            } else {
                cart.push({
                    title: currentCheckoutItem.title,
                    brand: currentCheckoutItem.brand,
                    variant: currentCheckoutItem.variant,
                    price: currentCheckoutItem.price,
                    image: mImg.src,
                    qty: 1
                });
            }
            
            updateCart();
            modalOverlay.classList.remove('active');
            cartOverlay.classList.add('active'); 
        };
        
        proceedToCheckoutBtn.onclick = () => {
            if(cart.length === 0) return;
            cartOverlay.classList.remove('active');
            
            const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
            const totalValue = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
            
            checkoutItemDesc.innerHTML = `<strong>Cart Summary:</strong> ${totalItems} items | <strong>Total: $${totalValue.toFixed(2)}</strong>`;
            
            checkoutOverlay.classList.add('active');
        };
        
        checkoutClose.onclick = () => {
            checkoutOverlay.classList.remove('active');
            document.body.style.overflow = '';
        };
        
        checkoutForm.onsubmit = async (e) => {
            e.preventDefault();
            cSubmit.disabled = true;
            cSubmit.textContent = "Processing...";
            checkoutFeedback.style.display = "block";
            checkoutFeedback.style.color = "#333";
            checkoutFeedback.textContent = "Securing order...";
            
            const dateStr = new Date().toISOString().slice(2,10).replace(/-/g,'');
            const rand4 = Math.floor(1000 + Math.random() * 9000);
            const orderId = `PX-${dateStr}-${rand4}`;
            
            const name = document.getElementById('c_name').value;
            const email = document.getElementById('c_email').value;
            const phone = document.getElementById('c_phone').value;
            const discordUser = document.getElementById('c_discord').value || "Not provided";
            const address = `${document.getElementById('c_address').value}, ${document.getElementById('c_city').value}, ${document.getElementById('c_state').value} ${document.getElementById('c_zip').value}`;
            
            let itemsString = cart.map(i => `${i.qty}x ${i.title} (${i.variant}) - $${(i.price * i.qty).toFixed(2)}`).join('\\n');
            if(itemsString.length > 900) { itemsString = itemsString.substring(0, 900) + '\\n...and more'; }
            
            const grandTotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0).toFixed(2);
            
            const payload = {
                username: "Pixie's Pantry Checkout",
                embeds: [{
                    title: `🛍️ New Order: ${orderId}`,
                    color: 13938487,
                    fields: [
                        { name: "Items Ordered", value: itemsString, inline: false },
                        { name: "Order Total", value: `$${grandTotal}`, inline: false },
                        { name: "Customer Name", value: name, inline: true },
                        { name: "Phone Number", value: phone, inline: true },
                        { name: "Discord", value: discordUser, inline: true },
                        { name: "Email", value: email, inline: false },
                        { name: "Shipping Address", value: address, inline: false }
                    ],
                    footer: { text: "Pixie's Pantry Automated Multi-Item Checkout" },
                    timestamp: new Date().toISOString()
                }]
            };
            
            try {
                const res = await fetch("https://discord.com/api/webhooks/1485836600381542481/opaZtBaCir8BV4fU55jzeBClzuQvXwVoL-P-kzhrepPmqghbhchcld_6SYZOtsRJ2Uw9", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                
                if(res.ok || res.status === 204) {
                    checkoutFeedback.style.color = "green";
                    checkoutFeedback.textContent = `Success! Order ID: ${orderId}. We will contact you for payment.`;
                    checkoutForm.reset();
                    cart = [];
                    updateCart();
                    
                    setTimeout(() => {
                        checkoutOverlay.classList.remove('active');
                        cSubmit.disabled = false;
                        cSubmit.textContent = "Submit Order";
                        checkoutFeedback.style.display = "none";
                        document.body.style.overflow = '';
                    }, 4000);
                } else {
                    throw new Error("Webhook failed");
                }
            } catch(err) {
                checkoutFeedback.style.color = "red";
                checkoutFeedback.textContent = "Error submitting order. Please try again or contact support.";
                cSubmit.disabled = false;
                cSubmit.textContent = "Submit Order";
            }
        };
        
        (function() {
            const overlay = document.getElementById('age-gate-overlay');
            if (!overlay) return;
            if (localStorage.getItem('pixies_age_verified') === 'true') {
                overlay.style.display = 'none';
            }
        })();
        window.ageGateEnter = function() {
            localStorage.setItem('pixies_age_verified', 'true');
            document.getElementById('age-gate-overlay').style.display = 'none';
        };
        window.ageGateDeny = function() {
            window.location.href = 'https://www.google.com';
        };

        updateCart();
        
        modalOverlay.onclick = (e) => { if(e.target === modalOverlay) modalClose.onclick(); };
        cartOverlay.onclick = (e) => { if(e.target === cartOverlay) cartClose.onclick(); };
        checkoutOverlay.onclick = (e) => { if(e.target === checkoutOverlay) checkoutClose.onclick(); };
    });
    """
    with open(os.path.join(OUTPUT_DIR, "js", "main.js"), "w") as f:
        f.write(js_content)

    def get_sidebar_html(depth=""):
        html = f"""
        <aside class="sidebar">
            <a href="{depth}index.html" class="sidebar-logo">Pixie's Pantry</a>
            <div class="sidebar-tagline">AirVape Collection</div>
            
            <a href="{depth}index.html" class="sidebar-link">All Products</a>
        """
        
        for brand in ["AirVape"]:
            html += f"""
            <div class="sidebar-section">{brand}</div>
            <a href="{depth}{brand.lower()}.html" class="sidebar-link">Shop All {brand}</a>
            """
            for cat in sorted(categories.get(brand, {}).keys()):
                if not cat: continue
                html += f'<a href="{depth}categories/{slugify(brand)}-{slugify(cat)}.html" class="sidebar-link child">{cat}</a>'
                
        html += f"""
            <div class="sidebar-community">
                <h4>Power in Numbers</h4>
                <p>Joining our Discord helps us demonstrate community engagement to distributors, unlocking cheaper wholesale prices that we pass directly to you.</p>
                <a href="{depth}community.html" class="link">Learn more</a>
                <a href="https://discord.gg/dm8deA2u" target="_blank" class="btn" style="background: var(--gold); color: #000; padding: 8px; font-size: 11px; width: 100%; box-sizing: border-box;">Join the Mission</a>
            </div>

            <div class="sidebar-footer">
                <a href="{depth}login.html" class="sidebar-link">Log In</a>
                <a href="{depth}signup.html" class="sidebar-link">Sign Up</a>
            </div>
        </aside>
        """
        return html

    def get_modal_html():
        return """
        <div class="cart-float" id="cart-float" title="View Cart">
            🛒<div class="cart-badge" id="cart-badge">0</div>
        </div>
        
        <div class="modal-overlay" id="cart-overlay">
            <div class="modal cart-modal">
                <button class="modal-close" id="cart-close">&times;</button>
                <h2 class="modal-title" style="margin-bottom: 5px;">Your Shopping Cart</h2>
                <div class="cart-items-container" id="cart-items-container">
                </div>
                <div class="cart-total-row">
                    <span>Total</span>
                    <span id="cart-total">$0.00</span>
                </div>
                <button class="btn" id="proceed-checkout-btn" style="width: 100%; padding: 15px; font-size: 16px;">Proceed to Checkout</button>
            </div>
        </div>

        <div class="modal-overlay" id="modal-overlay">
            <div class="modal">
                <button class="modal-close" id="modal-close">&times;</button>
                <div class="modal-left">
                    <img src="" alt="Product" class="modal-main-img" id="m-img">
                </div>
                <div class="modal-right">
                    <div class="modal-brand" id="m-brand">Brand</div>
                    <h2 class="modal-title" id="m-title">Product Name</h2>
                    <div class="modal-price" id="m-price">$0.00</div>
                    <div class="modal-desc" id="m-desc"></div>
                    
                    <div class="variant-label" id="v-label">Options</div>
                    <div class="swatch-group" id="swatches"></div>
                    
                    <button class="btn modal-buy-btn" id="add-to-cart-btn">Add to Cart</button>
                </div>
            </div>
        </div>
        
        <div class="modal-overlay" id="checkout-overlay">
            <div class="modal" style="max-width: 500px; flex-direction: column; padding: 40px;">
                <button class="modal-close" id="checkout-close">&times;</button>
                <h2 class="modal-title" style="margin-bottom: 5px;">Secure Checkout</h2>
                <div id="checkout-item-desc" style="margin-bottom: 25px; color: #444;"></div>
                <form id="checkout-form">
                    <div class="input-box"><label>Full Name *</label><input type="text" id="c_name" required></div>
                    <div class="input-box"><label>Email Address *</label><input type="email" id="c_email" required></div>
                    <div style="display: flex; gap: 15px;">
                        <div class="input-box" style="flex: 1;"><label>Phone Number *</label><input type="tel" id="c_phone" required></div>
                        <div class="input-box" style="flex: 1;"><label>Discord Username (Optional)</label><input type="text" id="c_discord" placeholder="e.g. user#1234"></div>
                    </div>
                    <div class="input-box">
                        <label>Shipping Address *</label>
                        <input type="text" id="c_address" placeholder="Street Address" required style="margin-bottom: 10px;">
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="c_city" placeholder="City" required style="flex: 2;">
                            <input type="text" id="c_state" placeholder="State" required style="flex: 1;">
                            <input type="text" id="c_zip" placeholder="ZIP" required style="flex: 1;">
                        </div>
                    </div>
                    <button type="submit" class="btn" style="width: 100%; margin-top: 15px; font-size: 15px; padding: 15px;" id="c_submit">Submit Order</button>
                </form>
                <div id="checkout-feedback" style="margin-top: 15px; font-size: 14px; font-weight: bold; text-align: center; display: none;"></div>
            </div>
        </div>
        """

    def render_page(filename, title, subtitle, product_list, depth=""):
        sidebar = get_sidebar_html(depth)
        modal = get_modal_html()
        
        products_dict = {p["handle"]: p for p in product_list}
        json_data = json.dumps(products_dict).replace("'", "\\'")
        
        grid_html = '<div class="grid">'
        for p in product_list:
            img = p.get("featured_image") or (p.get("all_images")[0] if p.get("all_images") else "https://via.placeholder.com/400")
            price = p.get("min_price", 0)
            handle = p["handle"]
            grid_html += f"""
            <div class="card" onclick="openModal('{handle}')">
                <img src="{img}" alt="{p['title']}" class="card-img" loading="lazy">
                <div class="card-body">
                    <div class="card-brand">{p['brand']}</div>
                    <h3 class="card-title">{p['title']}</h3>
                    <div class="card-price">${price:.2f}</div>
                    <span class="btn btn-outline" style="width:100%;box-sizing:border-box;">View Details</span>
                </div>
            </div>
            """
        grid_html += '</div>'
        if not product_list:
            grid_html = '<p>No products found in this category.</p>'
            
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} | Pixie's Pantry</title>
    <link rel="stylesheet" href="{depth}css/style.css">
</head>
<body>
    <div id="age-gate-overlay" class="age-gate-overlay">
        <div class="age-gate-box">
            <div class="age-gate-logo">PIXIE'S<span>PANTRY</span></div>
            <div class="age-gate-tagline">AirVape Collection</div>
            <h2 class="age-gate-title">ARE YOU 21 OR OLDER?</h2>
            <p class="age-gate-subtitle">You must be of legal age to enter this site. By entering, you agree to our Terms of Service and Privacy Policy.</p>
            <div class="age-gate-buttons">
                <button class="age-gate-yes" onclick="ageGateEnter()">Yes, I am 21+</button>
                <button class="age-gate-no" onclick="ageGateDeny()">No, I am not</button>
            </div>
            <p class="age-gate-disclaimer">Products are intended for use by adults of legal age in their respective jurisdiction.</p>
        </div>
    </div>
    
    <div class="banner">JOIN THE DISCORD FOR EXCLUSIVE WHOLESALE PRICING &nbsp;·&nbsp; <a href="https://discord.gg/dm8deA2u" target="_blank">DISCORD.GG/DM8DEa2U</a></div>
    {sidebar}
    <div class="main-wrapper">
        <main class="main-content">
            <h1 class="page-title">{title}</h1>
            <div class="page-subtitle">{subtitle}</div>
            {grid_html}
        </main>
        
        <footer class="site-footer">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>Pixie's Pantry</h3>
                    <p style="max-width: 300px;">Curating the absolute highest tier of vaporization and glass hardware. Direct wholesale access, vetted specifically for the community. Elevate your ritual.</p>
                </div>
                <div class="footer-col">
                    <h3>Explore</h3>
                    <ul>
                        <li><a href="{depth}index.html">Master Catalog</a></li>
                        <li><a href="javascript:void(0)" onclick="document.getElementById('cart-float').click()">View Cart</a></li>
                        <li><a href="{depth}community.html">Community Pricing</a></li>
                        <li><a href="https://dyspensr.com" target="_blank">Dyspensr Network</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Client Services</h3>
                    <ul>
                        <li><a href="https://discord.gg/dm8deA2u" target="_blank">Discord Support (Fastest)</a></li>
                        <li><a href="mailto:admin@pixies-pantry.com">Email Concierge</a></li>
                        <li><a href="{depth}shipping.html">Shipping & Delivery</a></li>
                        <li><a href="{depth}refunds.html">Returns & Exchanges</a></li>
                        <li><a href="{depth}privacy.html">Privacy & Terms</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Stay Exquisite</h3>
                    <p>Join the inner circle for exclusive drops and wholesale restocks.</p>
                    <form class="newsletter-form" action="https://formspree.io/f/xeoqkzdj" method="POST">
                        <input type="email" name="Newsletter Email" placeholder="Enter your email address" required>
                        <button type="submit">Subscribe</button>
                    </form>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 PIXIE'S PANTRY. ALL RIGHTS RESERVED.</p>
                <div class="footer-socials">
                    <a href="https://discord.gg/dm8deA2u" target="_blank">Discord</a>
                    <a href="#">Instagram</a>
                    <a href="#">Twitter</a>
                </div>
            </div>
        </footer>

    </div>
    {modal}
    <script>window.productsData = JSON.parse('{json_data}');</script>
    <script src="{depth}js/main.js"></script>
</body>
</html>"""
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(html)
            
    def render_community_page():
        sidebar = get_sidebar_html()
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Community Power & Pricing | Pixie's Pantry</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="banner">JOIN THE DISCORD FOR EXCLUSIVE WHOLESALE PRICING &nbsp;·&nbsp; <a href="https://discord.gg/dm8deA2u" target="_blank">DISCORD.GG/DM8DEa2U</a></div>
    {sidebar}
    <div class="main-wrapper">
        <main class="main-content" style="max-width: 800px;">
            <h1 class="page-title">Community Power & Pricing</h1>
            <div class="page-subtitle" style="color: var(--gold); font-weight: bold;">Unlock exclusive wholesale rates through community engagement.</div>
            
            <div style="font-size: 16px; line-height: 1.8; color: #333;">
                <p>At Pixie's Pantry, we believe in radical transparency. Here is the secret to the retail industry: <strong>Volume and community engagement dictate wholesale pricing.</strong></p>
                <p>When we approach distributors and manufacturers, they want to know one thing: do we have an active, engaged audience? The larger and more active our Discord community is, the more leverage we have to negotiate aggressive discounts on hardware.</p>
                <h3 style="margin-top: 30px; font-weight: 800;">How It Works</h3>
                <ul style="padding-left: 20px;">
                    <li style="margin-bottom: 10px;"><strong>Join the Discord:</strong> Every member adds weight to our bargaining power.</li>
                    <li style="margin-bottom: 10px;"><strong>We Negotiate:</strong> We show distributors our engagement metrics.</li>
                    <li style="margin-bottom: 10px;"><strong>You Save:</strong> The discounts we secure are passed directly to you on the storefront.</li>
                </ul>
                <p>By simply joining the Discord, you are actively helping lower the cost of premium AirVape hardware for yourself and everyone else.</p>
                <div style="margin-top: 40px; padding: 30px; background: #fafafa; border: 1px solid var(--border); border-radius: 12px; text-align: center;">
                    <h2 style="margin-top: 0;">Ready to lower prices?</h2>
                    <a href="https://discord.gg/dm8deA2u" target="_blank" class="btn" style="background: var(--gold); color: #000; font-size: 16px; padding: 15px 30px; margin-top: 15px;">Join the Mission on Discord</a>
                </div>
            </div>
        </main>
        
        <footer class="site-footer">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>Pixie's Pantry</h3>
                    <p style="max-width: 300px;">Curating the absolute highest tier of vaporization and glass hardware. Direct wholesale access, vetted specifically for the community. Elevate your ritual.</p>
                </div>
                <div class="footer-col">
                    <h3>Explore</h3>
                    <ul>
                        <li><a href="index.html">Master Catalog</a></li>
                        <li><a href="javascript:void(0)" onclick="document.getElementById('cart-float').click()">View Cart</a></li>
                        <li><a href="community.html">Community Pricing</a></li>
                        <li><a href="https://dyspensr.com" target="_blank">Dyspensr Network</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Client Services</h3>
                    <ul>
                        <li><a href="https://discord.gg/dm8deA2u" target="_blank">Discord Support (Fastest)</a></li>
                        <li><a href="mailto:admin@pixies-pantry.com">Email Concierge</a></li>
                        <li><a href="shipping.html">Shipping & Delivery</a></li>
                        <li><a href="refunds.html">Returns & Exchanges</a></li>
                        <li><a href="privacy.html">Privacy & Terms</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Stay Exquisite</h3>
                    <p>Join the inner circle for exclusive drops and wholesale restocks.</p>
                    <form class="newsletter-form" action="https://formspree.io/f/xeoqkzdj" method="POST">
                        <input type="email" name="Newsletter Email" placeholder="Enter your email address" required>
                        <button type="submit">Subscribe</button>
                    </form>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 PIXIE'S PANTRY. ALL RIGHTS RESERVED.</p>
                <div class="footer-socials">
                    <a href="https://discord.gg/dm8deA2u" target="_blank">Discord</a>
                    <a href="#">Instagram</a>
                    <a href="#">Twitter</a>
                </div>
            </div>
        </footer>

    </div>
</body>
</html>"""
        with open(os.path.join(OUTPUT_DIR, "community.html"), "w", encoding="utf-8") as f:
            f.write(html)

    print("Generating pages...")
    render_page("index.html", "Shop All", "Discover premium devices from AirVape.", products)
    render_page("airvape.html", "AirVape", "Advanced vaporizers and accessories.", brands.get("AirVape", []))
    
    for brand, cats in categories.items():
        for cat, prods in cats.items():
            if not cat: continue
            render_page(f"categories/{slugify(brand)}-{slugify(cat)}.html", 
                        f"{brand} {cat}", f"Shop all {brand} {cat}.", prods, depth="../")
                        
    auth_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Account | Pixie's Pantry</title>
    <link rel="stylesheet" href="css/style.css">
    <style>
        .auth-container { max-width: 400px; margin: 80px auto; text-align: center; }
        .input-box { margin-bottom: 20px; text-align: left; }
        .input-box label { display: block; font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; }
        .input-box input { width: 100%; border: 1px solid var(--border); padding: 12px; border-radius: 8px; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="banner">JOIN THE DISCORD FOR EXCLUSIVE WHOLESALE PRICING &nbsp;·&nbsp; <a href="https://discord.gg/dm8deA2u" target="_blank">DISCORD.GG/DM8DEa2U</a></div>
    {sidebar}
    <div class="main-wrapper">
        <main class="main-content">
            <div class="auth-container">
                <h1 class="page-title">{title}</h1>
                <p class="page-subtitle">FormPress Backend Required</p>
                <div class="input-box"><label>Email</label><input type="email"></div>
                <div class="input-box"><label>Password</label><input type="password"></div>
                <button class="btn" style="width:100%">{title}</button>
            </div>
        </main>
        
        <footer class="site-footer">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>Pixie's Pantry</h3>
                    <p style="max-width: 300px;">Curating the absolute highest tier of vaporization and glass hardware. Direct wholesale access, vetted specifically for the community. Elevate your ritual.</p>
                </div>
                <div class="footer-col">
                    <h3>Explore</h3>
                    <ul>
                        <li><a href="index.html">Master Catalog</a></li>
                        <li><a href="javascript:void(0)" onclick="document.getElementById('cart-float').click()">View Cart</a></li>
                        <li><a href="community.html">Community Pricing</a></li>
                        <li><a href="https://dyspensr.com" target="_blank">Dyspensr Network</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Client Services</h3>
                    <ul>
                        <li><a href="https://discord.gg/dm8deA2u" target="_blank">Discord Support (Fastest)</a></li>
                        <li><a href="mailto:admin@pixies-pantry.com">Email Concierge</a></li>
                        <li><a href="shipping.html">Shipping & Delivery</a></li>
                        <li><a href="refunds.html">Returns & Exchanges</a></li>
                        <li><a href="privacy.html">Privacy & Terms</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Stay Exquisite</h3>
                    <p>Join the inner circle for exclusive drops and wholesale restocks.</p>
                    <form class="newsletter-form" action="https://formspree.io/f/xeoqkzdj" method="POST">
                        <input type="email" name="Newsletter Email" placeholder="Enter your email address" required>
                        <button type="submit">Subscribe</button>
                    </form>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 PIXIE'S PANTRY. ALL RIGHTS RESERVED.</p>
                <div class="footer-socials">
                    <a href="https://discord.gg/dm8deA2u" target="_blank">Discord</a>
                    <a href="#">Instagram</a>
                    <a href="#">Twitter</a>
                </div>
            </div>
        </footer>

    </div>
</body>
</html>"""
    with open(os.path.join(OUTPUT_DIR, "login.html"), "w") as f:
        f.write(auth_html.replace("{sidebar}", get_sidebar_html()).replace("{title}", "Log In"))
    with open(os.path.join(OUTPUT_DIR, "signup.html"), "w") as f:
        f.write(auth_html.replace("{sidebar}", get_sidebar_html()).replace("{title}", "Sign Up"))

    render_community_page()
    print("Storefront generated successfully!")

if __name__ == "__main__":
    generate_site()