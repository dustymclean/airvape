
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
            
            let itemsString = cart.map(i => `${i.qty}x ${i.title} (${i.variant}) - $${(i.price * i.qty).toFixed(2)}`).join('\n');
            if(itemsString.length > 900) { itemsString = itemsString.substring(0, 900) + '\n...and more'; }
            
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
    