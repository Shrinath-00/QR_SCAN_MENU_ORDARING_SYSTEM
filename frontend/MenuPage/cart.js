let cart = [];
let isPlacingOrder = false;

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function addToCart(name, price) {
  const found = cart.find(i => i.name === name);
  found ? found.qty++ : cart.push({ name, price, qty: 1 });
  saveCart();
}

function increaseQty(name) {
  const item = cart.find(i => i.name === name);
  if (!item) return;
  item.qty++;
  saveCart();
}

function decreaseQty(name) {
  const item = cart.find(i => i.name === name);
  if (!item) return;
  item.qty--;
  if (item.qty <= 0) cart = cart.filter(i => i.name !== name);
  saveCart();
}

function saveCart() {
  updateCartBar();
  renderCart();
}

function updateCartBar() {
  let total = 0, count = 0;
  cart.forEach(i => { total += i.price * i.qty; count += i.qty; });
  const currency = (typeof CONFIG !== 'undefined' && CONFIG.cafe) ? CONFIG.cafe.currency_symbol : '₹';
  document.getElementById("cartCount").innerText = count + " items";
  document.getElementById("cartTotal").innerText = currency + total;
}

function openCartModal() {
  renderCart();
  new bootstrap.Modal(document.getElementById("cartModal")).show();
}

function renderCart() {
  const cartDiv = document.getElementById("cart");
  let html = "", total = 0;

  if (cart.length === 0) {
    cartDiv.innerHTML = '<p class="text-muted text-center" style="font-family:\'DM Mono\',monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;padding:20px 0;">Cart is empty</p>';
    const confirmBtnEmpty = document.querySelector('#cartModal .btn-success');
    if (confirmBtnEmpty) {
      confirmBtnEmpty.disabled = true;
      confirmBtnEmpty.style.opacity = '0.5';
    }
    return;
  }

  cart.forEach(item => {
    total += item.price * item.qty;
    html += '<div class="d-flex justify-content-between align-items-center mb-3">' +
      '<span style="font-size:14px;color:#1c2417;">' + escapeHtml(item.name) + '</span>' +
      '<div class="qty-control">' +
        '<button onclick="decreaseQty(\'' + escapeHtml(item.name).replace(/'/g, "\\'") + '\')">−</button>' +
        '<span>' + item.qty + '</span>' +
        '<button onclick="increaseQty(\'' + escapeHtml(item.name).replace(/'/g, "\\'") + '\')">+</button>' +
      '</div>' +
      '</div>';
  });

  const currency = (typeof CONFIG !== 'undefined' && CONFIG.cafe) ? CONFIG.cafe.currency_symbol : '₹';
  html += '<hr style="border-color:rgba(92,138,58,0.15);margin:16px 0;">' +
    '<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;">' +
      '<strong style="font-size:15px;color:#1c2417;">Total</strong>' +
      '<strong style="font-family:\'DM Mono\',monospace;font-size:16px;color:#5C8A3A;">' + currency + total + '</strong>' +
    '</div>';

  cartDiv.innerHTML = html;

  const confirmBtn = document.querySelector('#cartModal .btn-success');
  if (confirmBtn) {
    confirmBtn.disabled = false;
    confirmBtn.style.opacity = '1';
  }
}

function showOrderConfirmed(orderId, orderItems, orderTotal) {
  const modal = bootstrap.Modal.getInstance(document.getElementById("cartModal"));
  if (modal) modal.hide();

  const stale = document.getElementById("orderConfirmedOverlay");
  if (stale) stale.remove();

  const safeTableId = (typeof tableId !== 'undefined' && tableId) ? escapeHtml(String(tableId)) : '—';

  const overlay = document.createElement("div");
  overlay.id = "orderConfirmedOverlay";
  overlay.style.cssText = [
    "position:fixed;inset:0;z-index:9999;",
    "background:linear-gradient(rgba(255,255,255,0.82),rgba(255,255,255,0.82)),url('/assets/images/bg-pattern.png') center/cover fixed;",
    "display:flex;flex-direction:column;align-items:center;justify-content:center;",
    "padding:32px;text-align:center;font-family:'Noto Sans JP',sans-serif;overflow-y:auto;"
  ].join("");

  const currency = (typeof CONFIG !== 'undefined' && CONFIG.cafe) ? CONFIG.cafe.currency_symbol : '₹';
  const itemsList = orderItems.map(function(i) {
    return '<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(92,138,58,0.12);font-size:13px;color:#1c2417;">' +
      '<span>' + escapeHtml(i.name) + ' × ' + i.qty + '</span>' +
      '<span style="font-family:\'DM Mono\',monospace;color:#3a3a3a;">' + currency + (i.price * i.qty) + '</span>' +
      '</div>';
  }).join("");

  overlay.innerHTML =
    '<style>' +
      '@keyframes popIn{0%{transform:scale(0);opacity:0}60%{transform:scale(1.1)}100%{transform:scale(1);opacity:1}}' +
      '@keyframes fadeUp{0%{opacity:0;transform:translateY(16px)}100%{opacity:1;transform:translateY(0)}}' +
    '</style>' +
    '<div style="position:absolute;top:0;left:0;right:0;height:3px;background:#5C8A3A;"></div>' +
    '<div style="position:absolute;top:16px;right:16px;background:#5C8A3A;color:#fff;font-family:\'DM Mono\',monospace;font-size:9px;letter-spacing:2.5px;text-transform:uppercase;padding:5px 12px;border-radius:2px;">Table ' + safeTableId + '</div>' +
    '<div style="margin:0 auto 28px;animation:popIn 0.5s ease 0.2s both;">' +
      '<img src="../assets/images/caffe.png" alt="Aero Cafe" ' +
        'style="width:72px;height:72px;object-fit:contain;filter:drop-shadow(0 4px 16px rgba(92,138,58,0.25));" ' +
        'onerror="this.style.display=\'none\'" />' +
    '</div>' +
    '<div style="animation:fadeUp 0.5s ease 0.35s both;text-align:center;max-width:360px;width:100%;">' +
      '<div style="font-family:\'DM Mono\',monospace;font-size:9px;letter-spacing:5px;text-transform:uppercase;color:#5C8A3A;margin-bottom:14px;">Order Confirmed</div>' +
      '<div style="font-family:\'DM Mono\',monospace;font-size:22px;font-weight:500;letter-spacing:8px;text-transform:uppercase;color:#1c2417;margin-bottom:12px;">THANK YOU</div>' +
      '<div style="width:40px;height:1px;background:#5C8A3A;margin:0 auto 14px;"></div>' +
      '<div style="font-family:\'DM Mono\',monospace;font-size:10px;letter-spacing:2px;color:#777;margin-bottom:18px;">Order ' + escapeHtml(orderId) + '</div>' +
      '<div style="text-align:left;margin-bottom:18px;">' + itemsList + '</div>' +
      '<div style="display:flex;justify-content:space-between;align-items:center;padding-top:6px;border-top:1px solid rgba(92,138,58,0.2);">' +
        '<strong style="font-size:14px;color:#1c2417;">Total</strong>' +
        '<strong style="font-family:\'DM Mono\',monospace;font-size:16px;color:#5C8A3A;">' + currency + orderTotal + '</strong>' +
      '</div>' +
      '<div style="margin-top:24px;font-family:\'DM Mono\',monospace;font-size:11px;letter-spacing:2px;color:#999;">' +
        'Redirecting in <span id="cdNum">3</span>s' +
      '</div>' +
    '</div>';

  document.body.appendChild(overlay);

  let secs = 3;
  const cdInterval = setInterval(function() {
    secs--;
    const el = document.getElementById("cdNum");
    if (el) el.textContent = secs;
    if (secs <= 0) {
      clearInterval(cdInterval);
      window.location.href = "../index.html";
    }
  }, 1000);
}

async function confirmOrder() {
  if (cart.length === 0) return alert("Cart is empty!");
  if (isPlacingOrder) return;

  const confirmBtn = document.querySelector('#cartModal .btn-success');
  isPlacingOrder = true;
  confirmBtn.disabled = true;
  confirmBtn.innerText = "Placing order...";

  const orderId = "ORD" + Date.now();
  const orderTotal = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
  const orderItems = cart.map(i => ({ ...i }));

  const order = {
    order_id: orderId,
    table_id: (typeof tableId !== 'undefined') ? tableId : null,
    items: orderItems,
    status: "OPEN"
  };

  try {
    const res = await fetch(CONFIG.API_URL + "/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(order)
    });

    if (res.ok) {
      cart = [];
      saveCart();
      showOrderConfirmed(orderId, orderItems, orderTotal);
    } else {
      alert("Order could not be placed. Please try again.");
      confirmBtn.disabled = false;
      confirmBtn.innerText = "Confirm Order";
    }
  } catch (err) {
    console.error("Order error:", err);
    alert("Server connection error. Please try again.");
    confirmBtn.disabled = false;
    confirmBtn.innerText = "Confirm Order";
  } finally {
    isPlacingOrder = false;
  }
}
